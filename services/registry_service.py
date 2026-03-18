from common.tenancy import company_scoped_queryset
from logs.services import safe_create_system_log

from .models import RegisteredApplication, RegisteredFeature, RegisteredScreen, ServiceRegistry


def get_service_registry_queryset(*, user):
    queryset = ServiceRegistry.objects.filter(is_active=True).select_related("company")
    return company_scoped_queryset(queryset, user)


def get_registered_application_queryset(*, user):
    queryset = RegisteredApplication.objects.select_related("company")
    return company_scoped_queryset(queryset, user)


def get_registered_screen_queryset(*, user):
    queryset = RegisteredScreen.objects.select_related("application", "application__company")
    if user.is_superuser:
        return queryset
    if not user.is_authenticated:
        return queryset.none()
    return queryset.filter(application__company_id__in=user.company_ids)


def get_registered_feature_queryset(*, user):
    queryset = RegisteredFeature.objects.select_related(
        "application",
        "application__company",
        "screen",
    )
    if user.is_superuser:
        return queryset
    if not user.is_authenticated:
        return queryset.none()
    return queryset.filter(application__company_id__in=user.company_ids)


def log_registry_event(*, request, action, registry_type, instance):
    company_id = getattr(instance, "company_id", None)
    if company_id is None and hasattr(instance, "application"):
        company_id = instance.application.company_id

    safe_create_system_log(
        level="info",
        source=f"services.registry.{registry_type}",
        message=f"{registry_type} {action}",
        request_id=getattr(request, "request_id", ""),
        context={
            "action": action,
            "registry_type": registry_type,
            "instance_id": str(instance.pk),
            "company_id": str(company_id or ""),
            "user_id": str(getattr(request.user, "pk", "")),
        },
    )


def create_registry_entry(*, serializer, request, registry_type):
    instance = serializer.save()
    log_registry_event(request=request, action="created", registry_type=registry_type, instance=instance)
    return instance


def update_registry_entry(*, serializer, request, registry_type):
    instance = serializer.save()
    log_registry_event(request=request, action="updated", registry_type=registry_type, instance=instance)
    return instance


def deactivate_registry_entry(*, instance, request, registry_type):
    instance.is_active = False
    instance.save(update_fields=["is_active", "updated_at"])
    log_registry_event(request=request, action="deactivated", registry_type=registry_type, instance=instance)
    return instance
