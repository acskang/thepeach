import logging
import time
import uuid

from common.logging import request_id_context
from logs.services import safe_create_api_request_log, safe_create_system_log

request_logger = logging.getLogger("common.request")


class RequestContextLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.request_id = request_id
        token = request_id_context.set(request_id)
        started_at = time.monotonic()
        response = None

        try:
            response = self.get_response(request)
            return response
        except Exception as exc:
            if request.path.startswith("/api/"):
                safe_create_system_log(
                    level="error",
                    source="middleware.request",
                    message=str(exc),
                    request_id=request_id,
                    context={
                        "method": request.method,
                        "path": request.path,
                    },
                )
            raise
        finally:
            elapsed_ms = round((time.monotonic() - started_at) * 1000, 2)

            if response is not None:
                response["X-Request-ID"] = request_id

            if request.path.startswith("/api/"):
                safe_create_api_request_log(
                    request_id=request_id,
                    method=request.method,
                    path=request.path,
                    status_code=getattr(response, "status_code", 500),
                    duration_ms=elapsed_ms,
                    user=getattr(request, "user", None),
                    remote_addr=request.META.get("REMOTE_ADDR"),
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                )
                request_logger.info(
                    "method=%s path=%s status=%s duration_ms=%s user=%s",
                    request.method,
                    request.path,
                    getattr(response, "status_code", "error"),
                    elapsed_ms,
                    getattr(getattr(request, "user", None), "pk", "anonymous"),
                )

            request_id_context.reset(token)
