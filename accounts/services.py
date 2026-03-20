from django.conf import settings
from django.db.models import Count
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from logs.models import AuthEventLog
from logs.services import safe_create_auth_event_log


def log_auth_event(*, event_type, request, identifier="", user=None, success=True, detail=None):
    safe_create_auth_event_log(
        event_type=event_type,
        request_id=getattr(request, "request_id", ""),
        identifier=identifier,
        user=user,
        success=success,
        detail=detail or {},
    )


def get_auth_architecture_metadata():
    return {
        "login_mode": "local_jwt",
        "sso_ready": True,
        "future_extensions": [
            "oauth2-provider",
            "oidc-provider",
            "external-identity-provider",
            "service-trust",
        ],
    }


def build_public_auth_manifest():
    return {
        "module": "accounts",
        "zone": "public",
        "endpoints": {
            "signup": "/api/v1/auth/signup/",
            "login": "/api/v1/auth/login/",
            "refresh": "/api/v1/auth/token/refresh/",
            "logout": "/api/v1/auth/logout/",
            "me": "/api/v1/auth/me/",
            "internal_manifest": "/api/v1/auth/internal/",
        },
        "architecture": get_auth_architecture_metadata(),
    }


def build_internal_auth_manifest():
    return {
        "module": "accounts",
        "zone": "internal",
        "public_domain": settings.THEPEACH_PUBLIC_DOMAIN,
        "ops_domains": [
            settings.THEPEACH_OPS_DOMAIN,
            settings.THEPEACH_INTERNAL_AUTH_DOMAIN,
        ],
        "public_endpoints": {
            "root": "/api/v1/auth/",
            "signup": "/api/v1/auth/signup/",
            "login": "/api/v1/auth/login/",
            "refresh": "/api/v1/auth/token/refresh/",
            "logout": "/api/v1/auth/logout/",
            "me": "/api/v1/auth/me/",
        },
        "internal_endpoints": {
            "manifest": "/api/v1/auth/internal/",
            "auth_event_summary": "/api/v1/auth/internal/events/summary/",
        },
        "internal_access_policy": {
            "allowed_hosts": list(settings.THEPEACH_INTERNAL_ALLOWED_HOSTS),
            "required_headers": list(settings.THEPEACH_INTERNAL_REQUIRED_HEADERS),
        },
        "architecture": get_auth_architecture_metadata(),
    }


def log_signup_attempt(*, request, auth_logger):
    auth_logger.info("signup attempt identifier=%s", request.data.get("email", "unknown"))


def handle_signup(*, serializer, request, auth_logger):
    user = serializer.save()
    auth_logger.info("signup succeeded user=%s", user.pk)
    log_auth_event(
        event_type=AuthEventLog.EVENT_SIGNUP,
        request=request,
        identifier=user.email,
        user=user,
        success=True,
    )
    return user


def issue_login_tokens(*, serializer, request, auth_logger):
    try:
        serializer.is_valid(raise_exception=True)
    except exceptions.APIException as exc:
        auth_logger.warning("login failed identifier=%s", request.data.get("email", "unknown"))
        log_auth_event(
            event_type=AuthEventLog.EVENT_FAILURE,
            request=request,
            identifier=request.data.get("email", ""),
            success=False,
            detail={"reason": str(exc.detail)},
        )
        raise

    auth_logger.info("token issued identifier=%s", request.data.get("email", "unknown"))
    log_auth_event(
        event_type=AuthEventLog.EVENT_LOGIN,
        request=request,
        identifier=request.data.get("email", ""),
        user=serializer.user,
        success=True,
    )
    return Response(serializer.validated_data, status=status.HTTP_200_OK)


def refresh_tokens(*, request):
    serializer = TokenRefreshSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    log_auth_event(
        event_type=AuthEventLog.EVENT_TOKEN_REFRESH,
        request=request,
        success=True,
    )
    return serializer.validated_data


def get_auth_event_summary():
    aggregated = {
        item["event_type"]: item["total"]
        for item in AuthEventLog.objects.values("event_type").annotate(total=Count("id"))
    }
    return {
        "totals_by_event_type": aggregated,
        "successful_logins": AuthEventLog.objects.filter(
            event_type=AuthEventLog.EVENT_LOGIN,
            success=True,
        ).count(),
        "failed_attempts": AuthEventLog.objects.filter(
            event_type=AuthEventLog.EVENT_FAILURE,
            success=False,
        ).count(),
    }


def logout_user(*, serializer, request, auth_logger):
    serializer.is_valid(raise_exception=True)
    serializer.save()
    auth_logger.info("logout succeeded user=%s", request.user.pk)
    log_auth_event(
        event_type=AuthEventLog.EVENT_LOGOUT,
        request=request,
        identifier=request.user.email,
        user=request.user,
        success=True,
    )
