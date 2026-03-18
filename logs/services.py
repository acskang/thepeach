import logging

from logs.models import APIRequestLog, AuthEventLog, SystemLog

operations_logger = logging.getLogger("thepeach.operations")


def create_api_request_log(*, request_id, method, path, status_code, duration_ms, user=None, remote_addr=None, user_agent=""):
    return APIRequestLog.objects.create(
        request_id=request_id,
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
        user=user if getattr(user, "is_authenticated", False) else None,
        remote_addr=remote_addr,
        user_agent=user_agent or "",
    )


def safe_create_api_request_log(**kwargs):
    try:
        return create_api_request_log(**kwargs)
    except Exception:
        operations_logger.exception("Failed to persist API request log.")
        return None


def create_auth_event_log(*, event_type, request_id="", identifier="", user=None, success=True, detail=None):
    return AuthEventLog.objects.create(
        event_type=event_type,
        request_id=request_id,
        identifier=identifier or "",
        user=user if getattr(user, "is_authenticated", False) else user,
        success=success,
        detail=detail or {},
    )


def safe_create_auth_event_log(**kwargs):
    try:
        return create_auth_event_log(**kwargs)
    except Exception:
        operations_logger.exception("Failed to persist auth event log.")
        return None


def create_system_log(*, level, source, message, request_id="", context=None):
    return SystemLog.objects.create(
        level=level,
        source=source,
        message=message,
        request_id=request_id,
        context=context or {},
    )


def safe_create_system_log(**kwargs):
    try:
        return create_system_log(**kwargs)
    except Exception:
        operations_logger.exception("Failed to persist system log.")
        return None
