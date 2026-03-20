from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from core.exceptions import ThePeachAuthContractError, ThePeachAuthUnavailable

from .client import ThePeachAuthClient


class ThePeachRemoteUserMiddleware:
    """
    Middleware is kept lightweight and only hydrates request context for non-DRF views.
    It does not create or persist a local Django auth user.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.client = ThePeachAuthClient()

    def __call__(self, request):
        request.thepeach_auth = None
        request.thepeach_auth_error = None
        access_token = self._extract_access_token(request)
        if access_token:
            try:
                context = self.client.authenticate(
                    access_token=access_token,
                    request_headers={header: value for header, value in request.headers.items()},
                    request_host=request.get_host(),
                )
            except (ThePeachAuthUnavailable, ThePeachAuthContractError) as exc:
                request.thepeach_auth_error = exc
                request.user = AnonymousUser()
            else:
                request.thepeach_auth = context
                request.user = context.user if context.is_authenticated else AnonymousUser()
        return self.get_response(request)

    def _extract_access_token(self, request) -> str:
        authorization = request.headers.get("Authorization", "")
        if authorization:
            parts = authorization.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                return parts[1]
        return request.session.get(settings.THEPEACH_SESSION_TOKEN_KEY, "")
