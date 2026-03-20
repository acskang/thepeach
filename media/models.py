import os
from datetime import datetime
import uuid
from pathlib import Path

from django.conf import settings
from django.db import models
from django.utils.text import slugify

from common.models import BaseModel, CompanyOwnedModel


def shared_media_upload_to(instance, filename):
    original_name = Path(filename).name
    stem = slugify(Path(original_name).stem) or "asset"
    suffix = Path(original_name).suffix.lower() or ".bin"
    now = datetime.utcnow()
    return os.path.join(
        "shared",
        "images",
        now.strftime("%Y"),
        now.strftime("%m"),
        f"{stem}-{uuid.uuid4().hex}{suffix}",
    )


def platform_logo_upload_to(instance, filename):
    # Legacy compatibility for migration 0004_platformlogoasset.
    return shared_media_upload_to(instance, filename)


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


class SharedMediaAsset(BaseModel):
    KIND_IMAGE = "image"
    MEDIA_KIND_CHOICES = [
        (KIND_IMAGE, "Image"),
    ]

    file = models.FileField(upload_to=shared_media_upload_to)
    original_file_name = models.CharField(max_length=255)
    stored_file_name = models.CharField(max_length=255)
    file_size = models.PositiveBigIntegerField()
    mime_type = models.CharField(max_length=100)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    checksum_sha256 = models.CharField(max_length=64, db_index=True)
    title = models.CharField(max_length=200, blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    media_kind = models.CharField(max_length=20, choices=MEDIA_KIND_CHOICES, default=KIND_IMAGE)
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_shared_media_assets",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "created_at"], name="shared_media_act_idx"),
            models.Index(fields=["mime_type", "is_active"], name="shared_media_mime_idx"),
        ]

    def __str__(self):
        return self.title or self.original_file_name
