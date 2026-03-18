from django.db import models

from common.models import BaseModel, CompanyOwnedModel


class ServiceRegistry(CompanyOwnedModel):
    name = models.CharField(max_length=100)
    code = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    base_path = models.CharField(max_length=255)
    upstream_url = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    requires_authentication = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["company__name", "name"]
        verbose_name = "service registry entry"
        verbose_name_plural = "service registry entries"
        constraints = [
            models.UniqueConstraint(fields=["company", "code"], name="uniq_service_code_per_company"),
            models.UniqueConstraint(fields=["company", "base_path"], name="uniq_service_base_path_per_company"),
        ]

    def __str__(self):
        return f"{self.company.name} / {self.name} ({self.base_path})"


class RegisteredApplication(CompanyOwnedModel):
    app_code = models.SlugField(max_length=100, unique=True)
    app_name = models.CharField(max_length=200)
    app_description = models.TextField(blank=True)
    app_domain = models.CharField(max_length=255)
    app_base_url = models.URLField(max_length=500)
    is_active = models.BooleanField(default=True, db_index=True)
    requires_sso = models.BooleanField(default=True)

    class Meta:
        ordering = ["company__name", "app_name"]
        verbose_name = "registered application"
        verbose_name_plural = "registered applications"

    def __str__(self):
        return f"{self.company.name} / {self.app_name} ({self.app_code})"


class RegisteredScreen(BaseModel):
    application = models.ForeignKey(
        RegisteredApplication,
        on_delete=models.CASCADE,
        related_name="screens",
    )
    screen_code = models.SlugField(max_length=100)
    screen_name = models.CharField(max_length=200)
    route_path = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["application__app_name", "screen_name"]
        verbose_name = "registered screen"
        verbose_name_plural = "registered screens"
        constraints = [
            models.UniqueConstraint(fields=["application", "screen_code"], name="uniq_screen_code_per_application"),
            models.UniqueConstraint(fields=["application", "route_path"], name="uniq_screen_route_per_application"),
        ]

    def __str__(self):
        return f"{self.application.app_name} / {self.screen_name}"


class RegisteredFeature(BaseModel):
    TYPE_VIEW = "view"
    TYPE_ACTION = "action"
    TYPE_API = "api"
    TYPE_AUTOMATION = "automation"

    FEATURE_TYPE_CHOICES = [
        (TYPE_VIEW, "View"),
        (TYPE_ACTION, "Action"),
        (TYPE_API, "API"),
        (TYPE_AUTOMATION, "Automation"),
    ]

    application = models.ForeignKey(
        RegisteredApplication,
        on_delete=models.CASCADE,
        related_name="features",
    )
    screen = models.ForeignKey(
        RegisteredScreen,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="features",
    )
    feature_code = models.SlugField(max_length=100)
    feature_name = models.CharField(max_length=200)
    feature_type = models.CharField(max_length=32, choices=FEATURE_TYPE_CHOICES, default=TYPE_VIEW)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["application__app_name", "feature_name"]
        verbose_name = "registered feature"
        verbose_name_plural = "registered features"
        constraints = [
            models.UniqueConstraint(fields=["application", "feature_code"], name="uniq_feature_code_per_application"),
        ]

    def __str__(self):
        return f"{self.application.app_name} / {self.feature_name}"
