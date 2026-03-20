from rest_framework.permissions import BasePermission

from .internal_access import build_internal_access_context, log_internal_access_attempt


class InternalOnlyAccessPermission(BasePermission):
    message = "This endpoint is available only on internal operations hosts."

    def has_permission(self, request, view):
        context = build_internal_access_context(request)
        allowed = context["allowed"]
        log_internal_access_attempt(
            request=request,
            allowed=allowed,
            reason=context["failure_reason"] or "internal_permission_check",
            source=f"{view.__class__.__module__}.{view.__class__.__name__}",
        )
        return allowed
