import logging

from django.conf import settings

from logs.services import safe_create_system_log

security_logger = logging.getLogger("common.security")


def normalize_host(host: str) -> str:
    return host.split(":", 1)[0].strip().lower()


def get_request_host(request) -> str:
    host = request.META.get("HTTP_HOST") or request.get_host() or ""
    return normalize_host(host)


def get_internal_route_prefixes() -> tuple[str, ...]:
    return tuple(getattr(settings, "THEPEACH_INTERNAL_ROUTE_PREFIXES", ()))


def match_internal_route_prefix(path: str) -> str | None:
    for prefix in get_internal_route_prefixes():
        if path.startswith(prefix):
            return prefix
    return None


def is_internal_route(path: str) -> bool:
    return match_internal_route_prefix(path) is not None


def build_internal_access_context(request) -> dict:
    request_host = get_request_host(request)
    matched_prefix = match_internal_route_prefix(request.path)
    allowed_hosts = tuple(getattr(settings, "THEPEACH_INTERNAL_ALLOWED_HOSTS", ()))
    required_headers = tuple(getattr(settings, "THEPEACH_INTERNAL_REQUIRED_HEADERS", ()))
    missing_headers = tuple(
        header_name for header_name in required_headers if not request.headers.get(header_name)
    )

    allowed = bool(matched_prefix) and request_host in allowed_hosts and not missing_headers
    failure_reason = ""

    if not matched_prefix:
        failure_reason = "not_internal_path"
    elif request_host not in allowed_hosts:
        failure_reason = "invalid_host"
    elif missing_headers:
        failure_reason = "missing_required_headers"

    return {
        "allowed": allowed,
        "failure_reason": failure_reason,
        "host": request_host,
        "path": request.path,
        "matched_prefix": matched_prefix or "",
        "required_headers": list(required_headers),
        "missing_headers": list(missing_headers),
        "present_headers": {
            header_name: bool(request.headers.get(header_name))
            for header_name in required_headers
        },
    }


def log_internal_access_attempt(*, request, allowed: bool, reason: str = "", source: str = "internal.access"):
    context = build_internal_access_context(request)
    request_id = getattr(request, "request_id", "")
    user = getattr(request, "user", None)
    user_id = getattr(user, "pk", None) if getattr(user, "is_authenticated", False) else None

    context.update(
        {
            "method": request.method,
            "allowed": allowed,
            "reason": reason,
            "user_id": str(user_id) if user_id else "",
        }
    )

    level = "info" if allowed else "warning"
    message = "Internal route access granted." if allowed else "Internal route access denied."

    safe_create_system_log(
        level=level,
        source=source,
        message=message,
        request_id=request_id,
        context=context,
    )

    log_method = security_logger.info if allowed else security_logger.warning
    log_method(
        "allowed=%s reason=%s method=%s path=%s host=%s user=%s",
        allowed,
        reason or "-",
        request.method,
        request.path,
        context["host"],
        user_id or "anonymous",
    )

