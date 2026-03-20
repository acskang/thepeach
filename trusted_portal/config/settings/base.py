import os
from logging.handlers import WatchedFileHandler
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]


def env(key: str, default=None):
    return os.getenv(key, default)


def env_bool(key: str, default: bool = False) -> bool:
    value = os.getenv(key)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def env_list(key: str, default: str = "") -> list[str]:
    value = os.getenv(key, default)
    return [item.strip() for item in value.split(",") if item.strip()]


SECRET_KEY = env("TRUSTED_PORTAL_SECRET_KEY", "trusted-portal-local-dev-only")
DEBUG = env_bool("TRUSTED_PORTAL_DEBUG", False)
ALLOWED_HOSTS = env_list("TRUSTED_PORTAL_ALLOWED_HOSTS", "localhost,127.0.0.1")

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "rest_framework",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "core.auth.middleware.ThePeachRemoteUserMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = env("TRUSTED_PORTAL_TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOG_DIR = Path(env("TRUSTED_PORTAL_LOG_DIR", str(BASE_DIR / ".runtime" / "logs")))
LOG_DIR.mkdir(parents=True, exist_ok=True)

THEPEACH_BASE_URL = env("THEPEACH_BASE_URL", "https://thepeach.thesysm.com")
THEPEACH_FALLBACK_BASE_URLS = env_list("THEPEACH_FALLBACK_BASE_URLS", "")
THEPEACH_AUTH_LOGIN_PATH = env("THEPEACH_AUTH_LOGIN_PATH", "/api/v1/auth/login/")
THEPEACH_AUTH_ME_PATH = env("THEPEACH_AUTH_ME_PATH", "/api/v1/auth/me/")
THEPEACH_AUTH_TIMEOUT_SECONDS = float(env("THEPEACH_AUTH_TIMEOUT_SECONDS", "3.0"))
THEPEACH_SESSION_TOKEN_KEY = env("THEPEACH_SESSION_TOKEN_KEY", "thepeach_access_token")
THEPEACH_FORWARD_HEADERS = env_list("THEPEACH_FORWARD_HEADERS", "")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "core.auth.authentication.ThePeachRemoteAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    "EXCEPTION_HANDLER": "core.exceptions.api_exception_handler",
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "auth_file": {
            "class": "logging.handlers.WatchedFileHandler",
            "filename": str(LOG_DIR / "auth-debug.log"),
            "formatter": "standard",
        },
    },
    "loggers": {
        "trusted_portal.auth": {
            "handlers": ["console", "auth_file"],
            "level": env("TRUSTED_PORTAL_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}
