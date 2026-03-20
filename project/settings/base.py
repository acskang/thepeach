import os
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent.parent


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


SECRET_KEY = env("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if env_bool("DJANGO_ALLOW_INSECURE_SECRET_KEY", False):
        SECRET_KEY = "django-insecure-thepeach-local-dev-only"
    else:
        raise ImproperlyConfigured("DJANGO_SECRET_KEY must be configured.")

DEBUG = env_bool("DJANGO_DEBUG", False)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")
THEPEACH_PUBLIC_DOMAIN = env("THEPEACH_PUBLIC_DOMAIN", "thepeach.thesysm.com")
THEPEACH_OPS_DOMAIN = env("THEPEACH_OPS_DOMAIN", "ops.thesysm.com")
THEPEACH_INTERNAL_AUTH_DOMAIN = env("THEPEACH_INTERNAL_AUTH_DOMAIN", "auth-internal.thesysm.com")
THEPEACH_PUBLIC_BASE_URL = env("THEPEACH_PUBLIC_BASE_URL", f"https://{THEPEACH_PUBLIC_DOMAIN}")
THEPEACH_OPS_BASE_URL = env("THEPEACH_OPS_BASE_URL", f"https://{THEPEACH_OPS_DOMAIN}")
THEPEACH_INTERNAL_AUTH_BASE_URL = env(
    "THEPEACH_INTERNAL_AUTH_BASE_URL",
    f"https://{THEPEACH_INTERNAL_AUTH_DOMAIN}",
)
THEPEACH_INTERNAL_ALLOWED_HOSTS = tuple(
    env_list(
        "THEPEACH_INTERNAL_ALLOWED_HOSTS",
        f"{THEPEACH_OPS_DOMAIN},{THEPEACH_INTERNAL_AUTH_DOMAIN}",
    )
)
THEPEACH_INTERNAL_REQUIRED_HEADERS = tuple(env_list("THEPEACH_INTERNAL_REQUIRED_HEADERS"))
THEPEACH_INTERNAL_ROUTE_PREFIXES = (
    "/admin/",
    "/api/v1/auth/internal/",
    "/api/v1/gateway/internal/",
    "/api/v1/gateway/tools/",
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "common",
    "accounts",
    "gateway",
    "logs",
    "services",
    "media",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "common.middleware.RequestContextLoggingMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "common.middleware.InternalRouteAccessMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "project.wsgi.application"
ASGI_APPLICATION = "project.asgi.application"

POSTGRES_DB = env("POSTGRES_DB", "thepeach_db")
POSTGRES_USER = env("POSTGRES_USER", "cskang")
POSTGRES_PASSWORD = env("POSTGRES_PASSWORD", "")
POSTGRES_HOST = env("POSTGRES_HOST", "")
POSTGRES_PORT = env("POSTGRES_PORT", "5432")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": POSTGRES_DB,
        "USER": POSTGRES_USER,
        "PASSWORD": POSTGRES_PASSWORD,
        "HOST": POSTGRES_HOST,
        "PORT": POSTGRES_PORT,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = env("DJANGO_TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media_files"
THEPEACH_LOGO_MAX_UPLOAD_BYTES = int(env("THEPEACH_LOGO_MAX_UPLOAD_BYTES", str(5 * 1024 * 1024)))
THEPEACH_MEDIA_MAX_UPLOAD_BYTES = int(env("THEPEACH_MEDIA_MAX_UPLOAD_BYTES", str(THEPEACH_LOGO_MAX_UPLOAD_BYTES)))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "common.renderers.StandardJSONRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
    ),
    "DEFAULT_EXCEPTION_HANDLER": "common.exceptions.custom_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "common.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

LOG_DIR = Path(env("DJANGO_LOG_DIR", str(BASE_DIR / ".runtime" / "logs")))
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "platform": {
            "format": "%(asctime)s %(levelname)s %(name)s request_id=%(request_id)s %(message)s",
        },
        "error": {
            "format": "%(asctime)s %(levelname)s %(name)s request_id=%(request_id)s %(message)s",
        },
    },
    "filters": {
        "request_context": {
            "()": "common.logging.RequestContextFilter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "platform",
            "filters": ["request_context"],
        },
        "app_file": {
            "class": "logging.handlers.WatchedFileHandler",
            "filename": str(LOG_DIR / "application.log"),
            "formatter": "platform",
            "filters": ["request_context"],
        },
        "error_file": {
            "class": "logging.handlers.WatchedFileHandler",
            "filename": str(LOG_DIR / "error.log"),
            "formatter": "error",
            "filters": ["request_context"],
        },
        "auth_file": {
            "class": "logging.handlers.WatchedFileHandler",
            "filename": str(LOG_DIR / "auth.log"),
            "formatter": "platform",
            "filters": ["request_context"],
        },
        "api_file": {
            "class": "logging.handlers.WatchedFileHandler",
            "filename": str(LOG_DIR / "api.log"),
            "formatter": "platform",
            "filters": ["request_context"],
        },
        "security_file": {
            "class": "logging.handlers.WatchedFileHandler",
            "filename": str(LOG_DIR / "security.log"),
            "formatter": "platform",
            "filters": ["request_context"],
        },
    },
    "root": {
        "handlers": ["console", "app_file"],
        "level": env("DJANGO_LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "common.request": {
            "handlers": ["console", "api_file"],
            "level": env("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "accounts.auth": {
            "handlers": ["console", "auth_file"],
            "level": env("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "common.security": {
            "handlers": ["console", "security_file"],
            "level": env("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "common.docs": {
            "handlers": ["console", "app_file"],
            "level": env("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "media.asset": {
            "handlers": ["console", "app_file"],
            "level": env("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "thepeach.operations": {
            "handlers": ["console", "error_file"],
            "level": env("DJANGO_LOG_LEVEL", "WARNING"),
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", "error_file"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
