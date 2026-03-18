from django.conf import settings
from django.db import models

from common.models import BaseModel


class APIRequestLog(BaseModel):
    request_id = models.CharField(max_length=64, db_index=True)
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=512, db_index=True)
    status_code = models.PositiveIntegerField()
    duration_ms = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="api_request_logs",
    )
    remote_addr = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["path", "created_at"]),
            models.Index(fields=["status_code", "created_at"]),
        ]


class AuthEventLog(BaseModel):
    EVENT_LOGIN = "login"
    EVENT_LOGOUT = "logout"
    EVENT_SIGNUP = "signup"
    EVENT_TOKEN_REFRESH = "token_refresh"
    EVENT_TOKEN_VERIFY = "token_verify"
    EVENT_FAILURE = "failure"

    EVENT_CHOICES = [
        (EVENT_LOGIN, "Login"),
        (EVENT_LOGOUT, "Logout"),
        (EVENT_SIGNUP, "Signup"),
        (EVENT_TOKEN_REFRESH, "Token Refresh"),
        (EVENT_TOKEN_VERIFY, "Token Verify"),
        (EVENT_FAILURE, "Failure"),
    ]

    request_id = models.CharField(max_length=64, db_index=True, blank=True)
    event_type = models.CharField(max_length=32, choices=EVENT_CHOICES, db_index=True)
    identifier = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="auth_event_logs",
    )
    success = models.BooleanField(default=True, db_index=True)
    detail = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
            models.Index(fields=["success", "created_at"]),
        ]


class SystemLog(BaseModel):
    LEVEL_DEBUG = "debug"
    LEVEL_INFO = "info"
    LEVEL_WARNING = "warning"
    LEVEL_ERROR = "error"
    LEVEL_CRITICAL = "critical"

    LEVEL_CHOICES = [
        (LEVEL_DEBUG, "Debug"),
        (LEVEL_INFO, "Info"),
        (LEVEL_WARNING, "Warning"),
        (LEVEL_ERROR, "Error"),
        (LEVEL_CRITICAL, "Critical"),
    ]

    request_id = models.CharField(max_length=64, db_index=True, blank=True)
    level = models.CharField(max_length=16, choices=LEVEL_CHOICES, db_index=True)
    source = models.CharField(max_length=128, db_index=True)
    message = models.TextField()
    context = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["level", "created_at"]),
            models.Index(fields=["source", "created_at"]),
        ]
