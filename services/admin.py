from django.contrib import admin

from .models import RegisteredApplication, RegisteredFeature, RegisteredScreen, ServiceRegistry


@admin.register(ServiceRegistry)
class ServiceRegistryAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "code", "base_path", "is_active", "requires_authentication", "created_at")
    list_filter = ("company", "is_active", "requires_authentication", "created_at")
    search_fields = ("name", "code", "base_path", "company__name")


@admin.register(RegisteredApplication)
class RegisteredApplicationAdmin(admin.ModelAdmin):
    list_display = ("app_name", "app_code", "company", "app_domain", "is_active", "requires_sso", "created_at")
    list_filter = ("company", "is_active", "requires_sso", "created_at")
    search_fields = ("app_name", "app_code", "app_domain", "company__name")


@admin.register(RegisteredScreen)
class RegisteredScreenAdmin(admin.ModelAdmin):
    list_display = ("screen_name", "screen_code", "application", "route_path", "is_active", "created_at")
    list_filter = ("application__company", "application", "is_active", "created_at")
    search_fields = ("screen_name", "screen_code", "route_path", "application__app_name", "application__app_code")


@admin.register(RegisteredFeature)
class RegisteredFeatureAdmin(admin.ModelAdmin):
    list_display = ("feature_name", "feature_code", "application", "screen", "feature_type", "is_active", "created_at")
    list_filter = ("application__company", "application", "feature_type", "is_active", "created_at")
    search_fields = ("feature_name", "feature_code", "application__app_name", "screen__screen_name")
