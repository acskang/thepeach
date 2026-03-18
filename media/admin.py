from django.contrib import admin

from .models import MediaAsset, PlatformLogoAsset


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "asset_type", "source_type", "is_public", "is_reusable", "created_at")
    list_filter = ("company", "asset_type", "source_type", "is_public", "is_reusable", "created_at")
    search_fields = ("title", "slug", "description", "alt_text", "company__name")


@admin.register(PlatformLogoAsset)
class PlatformLogoAssetAdmin(admin.ModelAdmin):
    list_display = ("logo_name", "logo_code", "application", "usage_type", "is_active", "created_at")
    list_filter = ("application__company", "application", "usage_type", "is_active", "created_at")
    search_fields = ("logo_name", "logo_code", "application__app_name", "application__app_code", "alt_text")
