import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

os.environ.setdefault("DJANGO_ALLOW_INSECURE_SECRET_KEY", "true")
os.environ.setdefault("DJANGO_SECRET_KEY", "django-insecure-thepeach-local-dev-only")
os.environ.setdefault("DJANGO_DEBUG", "true")
os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost")
os.environ.setdefault(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "http://127.0.0.1:8000,http://localhost:8000",
)
os.environ.setdefault("DJANGO_LOG_DIR", str(BASE_DIR / ".runtime" / "logs"))

from .base import *  # noqa: F401,F403
