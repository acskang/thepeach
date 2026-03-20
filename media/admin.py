from django.contrib import admin

from .models import MediaAsset, SharedMediaAsset


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "asset_type", "source_type", "is_public", "is_reusable", "created_at")
    list_filter = ("company", "asset_type", "source_type", "is_public", "is_reusable", "created_at")
    search_fields = ("title", "slug", "description", "alt_text", "company__name")


@admin.register(SharedMediaAsset)
class SharedMediaAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "original_file_name", "mime_type", "file_size", "is_active", "created_at")
    list_filter = ("mime_type", "media_kind", "is_active", "created_at")
    search_fields = ("title", "original_file_name", "stored_file_name", "checksum_sha256", "alt_text", "description")
