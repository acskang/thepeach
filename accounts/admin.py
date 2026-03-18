from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Company, Department, User, UserCompanyMembership, UserDepartmentMembership


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = ("email", "full_name", "display_name", "smartphone_number", "is_staff", "is_active", "created_at")
    search_fields = ("email", "full_name", "display_name", "external_id", "smartphone_number")
    readonly_fields = ("created_at", "updated_at", "last_login")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("full_name", "display_name", "first_name", "last_name", "smartphone_number", "external_id")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "full_name", "display_name", "smartphone_number", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "code")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "company", "is_active", "created_at")
    list_filter = ("company", "is_active", "created_at")
    search_fields = ("name", "code", "company__name")


@admin.register(UserCompanyMembership)
class UserCompanyMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "role", "is_default", "created_at")
    list_filter = ("role", "is_default", "company", "created_at")
    search_fields = ("user__email", "company__name")


@admin.register(UserDepartmentMembership)
class UserDepartmentMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "department", "role", "created_at")
    list_filter = ("role", "department__company", "created_at")
    search_fields = ("user__email", "department__name", "department__company__name")
