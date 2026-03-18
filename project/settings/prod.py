from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403

if DEBUG:
    raise ImproperlyConfigured("Production settings must not run with DEBUG=True.")

if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS must be configured for production.")

if not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = [
        "https://thesysm.com",
        "https://*.thesysm.com",
    ]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
SECURE_HSTS_SECONDS = int(env("DJANGO_SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", True)
SECURE_HSTS_PRELOAD = env_bool("DJANGO_SECURE_HSTS_PRELOAD", True)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"

LOG_DIR = Path(env("DJANGO_LOG_DIR", "/logs/thepeach"))
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING["handlers"]["app_file"]["filename"] = str(LOG_DIR / "application.log")
LOGGING["handlers"]["error_file"]["filename"] = str(LOG_DIR / "error.log")
LOGGING["handlers"]["auth_file"]["filename"] = str(LOG_DIR / "auth.log")
LOGGING["handlers"]["api_file"]["filename"] = str(LOG_DIR / "api.log")
