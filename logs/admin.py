from django.contrib import admin

from .models import APIRequestLog, AuthEventLog, SystemLog


@admin.register(APIRequestLog)
class APIRequestLogAdmin(admin.ModelAdmin):
    list_display = ("request_id", "method", "path", "status_code", "duration_ms", "user", "created_at")
    list_filter = ("method", "status_code", "created_at")
    search_fields = ("request_id", "path", "user__email")
    readonly_fields = [field.name for field in APIRequestLog._meta.fields]


@admin.register(AuthEventLog)
class AuthEventLogAdmin(admin.ModelAdmin):
    list_display = ("event_type", "identifier", "user", "success", "request_id", "created_at")
    list_filter = ("event_type", "success", "created_at")
    search_fields = ("identifier", "request_id", "user__email")
    readonly_fields = [field.name for field in AuthEventLog._meta.fields]


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ("level", "source", "request_id", "created_at")
    list_filter = ("level", "source", "created_at")
    search_fields = ("message", "request_id", "source")
    readonly_fields = [field.name for field in SystemLog._meta.fields]
