from django.shortcuts import render
from django.conf import settings
from rest_framework import status
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.views import APIView

from core.auth.client import ThePeachAuthClient
from core.auth.permissions import HasThePeachAuthenticatedUser
from core.responses import error_response, success_response


def home(request):
    user = request.user if getattr(request.user, "is_authenticated", False) else None
    return render(
        request,
        "core/home.html",
        {
            "service_name": "Trusted Portal",
            "auth_source": getattr(getattr(request, "thepeach_auth", None), "source", "none"),
            "user": user,
        },
    )


def login_page(request):
    user = request.user if getattr(request.user, "is_authenticated", False) else None
    return render(
        request,
        "core/login.html",
        {
            "user": user,
        },
    )


class AuthStatusAPIView(APIView):
    permission_classes = [HasThePeachAuthenticatedUser]

    def get(self, request, *args, **kwargs):
        auth_context = getattr(request, "thepeach_auth", None)
        return success_response(
            {
                "authenticated": True,
                "source": getattr(auth_context, "source", "thepeach_api"),
                "user": request.user.to_dict(),
            }
        )


class AuthMeAPIView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "core/auth_me.html"

    def get(self, request, *args, **kwargs):
        is_authenticated = bool(getattr(request.user, "is_authenticated", False))
        auth_context = getattr(request, "thepeach_auth", None)
        payload = {
            "authenticated": is_authenticated,
            "source": getattr(auth_context, "source", "none"),
            "user": request.user.to_dict() if is_authenticated else None,
            "upstream_contract": "/api/v1/auth/me/",
        }
        if request.accepted_renderer.format == "html":
            return render(
                request,
                self.template_name,
                {
                    "payload": payload,
                    "user": request.user if is_authenticated else None,
                },
            )
        if not is_authenticated:
            return error_response(
                "A valid ThePeach access token is required.",
                code="not_authenticated",
                status_code=401,
            )
        return success_response(payload)


class SessionLoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = str(request.data.get("email", "")).strip()
        password = str(request.data.get("password", ""))
        if not email or not password:
            return error_response(
                "Email and password are required.",
                code="invalid_credentials",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        client = ThePeachAuthClient()
        login_data = client.login(
            email=email,
            password=password,
            request_headers={header: value for header, value in request.headers.items()},
            request_host=request.get_host(),
        )
        access_token = login_data.get("access", "")
        if not access_token:
            return error_response(
                "ThePeach login response did not include an access token.",
                code="thepeach_auth_contract_error",
                status_code=status.HTTP_502_BAD_GATEWAY,
            )
        request.session[settings.THEPEACH_SESSION_TOKEN_KEY] = access_token
        request.session.modified = True
        return success_response(
            {
                "logged_in": True,
                "user": login_data.get("user"),
                "source": "thepeach_api",
            }
        )


class SessionLogoutAPIView(APIView):
    def post(self, request, *args, **kwargs):
        request.session.pop(settings.THEPEACH_SESSION_TOKEN_KEY, None)
        request.session.modified = True
        return success_response({"logged_out": True})
