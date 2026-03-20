from django.conf import settings
from rest_framework import authentication, exceptions

from .client import ThePeachAuthClient


class ThePeachRemoteAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        access_token = self._extract_access_token(request)
        if not access_token:
            return None

        cached_error = getattr(request, "thepeach_auth_error", None)
        if cached_error is not None:
            raise cached_error

        cached_context = getattr(request, "thepeach_auth", None)
        if cached_context is not None and getattr(cached_context, "access_token", "") == access_token:
            if not cached_context.is_authenticated:
                raise exceptions.AuthenticationFailed(cached_context.error_message or "Authentication failed.")
            return cached_context.user, cached_context

        client = ThePeachAuthClient()
        context = client.authenticate(
            access_token=access_token,
            request_headers={header: value for header, value in request.headers.items()},
            request_host=request.get_host(),
        )
        request.thepeach_auth = context

        if not context.is_authenticated:
            raise exceptions.AuthenticationFailed(context.error_message or "Authentication failed.")

        return context.user, context

    def _extract_access_token(self, request) -> str:
        header_value = authentication.get_authorization_header(request).decode("utf-8")
        if header_value:
            parts = header_value.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                return parts[1]

        return request.session.get(settings.THEPEACH_SESSION_TOKEN_KEY, "")
