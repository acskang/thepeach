import hashlib
from pathlib import Path

import django.db.models.deletion
import media.models
import uuid
from django.conf import settings
from django.db import migrations, models


def copy_logo_assets_to_shared_media(apps, schema_editor):
    PlatformLogoAsset = apps.get_model("media", "PlatformLogoAsset")
    SharedMediaAsset = apps.get_model("media", "SharedMediaAsset")

    for logo in PlatformLogoAsset.objects.all().iterator():
        checksum = ""
        if logo.image_file:
            try:
                hasher = hashlib.sha256()
                with logo.image_file.open("rb") as source:
                    for chunk in iter(lambda: source.read(8192), b""):
                        hasher.update(chunk)
                checksum = hasher.hexdigest()
            except OSError:
                checksum = ""

        SharedMediaAsset.objects.create(
            id=logo.id,
            created_at=logo.created_at,
            updated_at=logo.updated_at,
            file=logo.image_file.name if logo.image_file else "",
            original_file_name=logo.original_file_name,
            stored_file_name=Path(logo.image_file.name).name if logo.image_file else "",
            file_size=logo.file_size,
            mime_type=logo.mime_type,
            width=logo.width,
            height=logo.height,
            checksum_sha256=checksum,
            title=logo.logo_name,
            alt_text=logo.alt_text,
            description="",
            media_kind="image",
            is_active=logo.is_active,
            created_by_id=logo.created_by_id,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("media", "0004_platformlogoasset"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SharedMediaAsset",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("file", models.FileField(upload_to=media.models.shared_media_upload_to)),
                ("original_file_name", models.CharField(max_length=255)),
                ("stored_file_name", models.CharField(max_length=255)),
                ("file_size", models.PositiveBigIntegerField()),
                ("mime_type", models.CharField(max_length=100)),
                ("width", models.PositiveIntegerField()),
                ("height", models.PositiveIntegerField()),
                ("checksum_sha256", models.CharField(db_index=True, max_length=64)),
                ("title", models.CharField(blank=True, max_length=200)),
                ("alt_text", models.CharField(blank=True, max_length=255)),
                ("description", models.TextField(blank=True)),
                ("media_kind", models.CharField(choices=[("image", "Image")], default="image", max_length=20)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_shared_media_assets",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["is_active", "created_at"], name="shared_media_act_idx"),
                    models.Index(fields=["mime_type", "is_active"], name="shared_media_mime_idx"),
                ],
            },
        ),
        migrations.RunPython(copy_logo_assets_to_shared_media, migrations.RunPython.noop),
        migrations.DeleteModel(name="PlatformLogoAsset"),
    ]
