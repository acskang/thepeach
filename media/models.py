import os
import uuid
from pathlib import Path

from django.conf import settings
from django.db import models
from django.utils.text import slugify

from common.models import BaseModel, CompanyOwnedModel


def platform_logo_upload_to(instance, filename):
    original_name = Path(filename).name
    stem = slugify(Path(original_name).stem) or "logo"
    suffix = Path(original_name).suffix.lower() or ".bin"
    app_code = getattr(instance.application, "app_code", "unassigned")
    return os.path.join("logos", app_code, f"{stem}-{uuid.uuid4().hex}{suffix}")


class MediaAsset(CompanyOwnedModel):
    TYPE_IMAGE = "image"
    TYPE_LOGO = "logo"
    TYPE_VIDEO = "video"

    TYPE_CHOICES = [
        (TYPE_IMAGE, "Image"),
        (TYPE_LOGO, "Logo"),
        (TYPE_VIDEO, "Video"),
    ]

    SOURCE_FILE = "file"
    SOURCE_URL = "url"
    SOURCE_EMBED = "embed"

    SOURCE_CHOICES = [
        (SOURCE_FILE, "File"),
        (SOURCE_URL, "URL"),
        (SOURCE_EMBED, "Embed"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    asset_type = models.CharField(max_length=20, choices=TYPE_CHOICES, db_index=True)
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=SOURCE_URL)
    file = models.FileField(upload_to="assets/%Y/%m/", blank=True, null=True)
    source_url = models.URLField(max_length=500, blank=True)
    embed_url = models.URLField(max_length=500, blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True, db_index=True)
    is_reusable = models.BooleanField(default=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["company__name", "title"]
        indexes = [
            models.Index(fields=["company", "asset_type", "is_public"], name="media_company_public_idx"),
            models.Index(fields=["company", "asset_type", "is_reusable"], name="media_company_reusable_idx"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["company", "slug"], name="uniq_media_slug_per_company"),
        ]

    def __str__(self):
        return f"{self.company.name} / {self.title} ({self.asset_type})"


class PlatformLogoAsset(BaseModel):
    TYPE_PRIMARY = "primary"
    TYPE_HEADER = "header"
    TYPE_ICON = "icon"
    TYPE_DARK_MODE = "dark_mode"
    TYPE_LIGHT_MODE = "light_mode"

    USAGE_TYPE_CHOICES = [
        (TYPE_PRIMARY, "Primary"),
        (TYPE_HEADER, "Header"),
        (TYPE_ICON, "Icon"),
        (TYPE_DARK_MODE, "Dark Mode"),
        (TYPE_LIGHT_MODE, "Light Mode"),
    ]

    application = models.ForeignKey(
        "services.RegisteredApplication",
        on_delete=models.PROTECT,
        related_name="logo_assets",
    )
    logo_code = models.SlugField(max_length=100, unique=True)
    logo_name = models.CharField(max_length=200)
    original_file_name = models.CharField(max_length=255)
    image_file = models.FileField(upload_to=platform_logo_upload_to)
    file_size = models.PositiveBigIntegerField()
    mime_type = models.CharField(max_length=100)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    alt_text = models.CharField(max_length=255, blank=True)
    usage_type = models.CharField(max_length=32, choices=USAGE_TYPE_CHOICES, default=TYPE_PRIMARY)
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_logo_assets",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_logo_assets",
    )

    class Meta:
        ordering = ["application__app_name", "logo_name"]
        indexes = [
            models.Index(fields=["application", "is_active"], name="logo_app_active_idx"),
            models.Index(fields=["application", "usage_type"], name="logo_app_usage_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["application", "usage_type"],
                condition=models.Q(is_active=True, usage_type="primary"),
                name="uniq_active_primary_logo_per_application",
            ),
        ]

    def __str__(self):
        return f"{self.application.app_name} / {self.logo_name} ({self.logo_code})"
