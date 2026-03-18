import logging
from pathlib import Path

from django.conf import settings
from PIL import Image, UnidentifiedImageError
from rest_framework.exceptions import PermissionDenied, ValidationError

from common.tenancy import validate_department_access
from logs.services import safe_create_system_log

from .models import PlatformLogoAsset

logo_logger = logging.getLogger("media.logo")

ALLOWED_PIL_FORMATS = {
    "PNG": "image/png",
    "JPEG": "image/jpeg",
}


def _log_logo_event(*, request, action, instance=None, detail=None, level="info"):
    safe_create_system_log(
        level=level,
        source="media.logo",
        message=f"logo {action}",
        request_id=getattr(request, "request_id", ""),
        context={
            "action": action,
            "logo_id": str(instance.pk) if instance else "",
            "logo_code": getattr(instance, "logo_code", ""),
            "application_code": getattr(getattr(instance, "application", None), "app_code", ""),
            "user_id": str(getattr(request.user, "pk", "")),
            "detail": detail or {},
        },
    )


def get_logo_queryset(*, user, application_code=None, usage_type=None, is_active=None):
    queryset = PlatformLogoAsset.objects.select_related(
        "application",
        "application__company",
        "created_by",
        "updated_by",
    )

    if user.is_superuser:
        scoped = queryset
    elif user.is_authenticated:
        scoped = queryset.filter(application__company_id__in=user.company_ids)
    else:
        scoped = queryset.none()

    if application_code:
        scoped = scoped.filter(application__app_code=application_code)
    if usage_type:
        scoped = scoped.filter(usage_type=usage_type)
    if is_active is not None:
        scoped = scoped.filter(is_active=is_active)

    return scoped


def validate_logo_upload(*, uploaded_file, request, application):
    logo_logger.info(
        "logo upload attempt application=%s filename=%s size=%s",
        application.app_code,
        getattr(uploaded_file, "name", ""),
        getattr(uploaded_file, "size", 0),
    )

    if uploaded_file is None:
        _log_logo_event(request=request, action="validation_failed", detail={"reason": "missing_file"}, level="warning")
        raise ValidationError({"image_file": "image_file is required."})

    if uploaded_file.size <= 0:
        _log_logo_event(request=request, action="validation_failed", detail={"reason": "empty_file"}, level="warning")
        raise ValidationError({"image_file": "Uploaded file cannot be empty."})

    max_size = getattr(settings, "THEPEACH_LOGO_MAX_UPLOAD_BYTES", 5 * 1024 * 1024)
    if uploaded_file.size > max_size:
        _log_logo_event(
            request=request,
            action="validation_failed",
            detail={"reason": "oversized_file", "size": uploaded_file.size},
            level="warning",
        )
        raise ValidationError({"image_file": f"Logo files must be {max_size} bytes or smaller."})

    try:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        image.verify()
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        pil_format = image.format
        width, height = image.size
    except (UnidentifiedImageError, OSError, ValueError):
        _log_logo_event(
            request=request,
            action="validation_failed",
            detail={"reason": "corrupted_or_invalid_image"},
            level="warning",
        )
        raise ValidationError({"image_file": "Uploaded file is not a valid image."})
    finally:
        uploaded_file.seek(0)

    if pil_format not in ALLOWED_PIL_FORMATS:
        _log_logo_event(
            request=request,
            action="validation_failed",
            detail={"reason": "unsupported_type", "format": pil_format},
            level="warning",
        )
        raise ValidationError({"image_file": "Only PNG and JPEG logo files are allowed."})

    mime_type = ALLOWED_PIL_FORMATS[pil_format]
    original_name = Path(getattr(uploaded_file, "name", "logo")).name

    return {
        "original_file_name": original_name,
        "file_size": uploaded_file.size,
        "mime_type": mime_type,
        "width": width,
        "height": height,
    }


def create_logo_asset(*, serializer, request):
    application = serializer.validated_data["application"]
    validate_department_access(user=request.user, company=application.company)
    metadata = validate_logo_upload(
        uploaded_file=serializer.validated_data["image_file"],
        request=request,
        application=application,
    )

    instance = serializer.save(
        created_by=request.user,
        updated_by=request.user,
        **metadata,
    )
    logo_logger.info("logo upload success logo=%s application=%s", instance.logo_code, application.app_code)
    _log_logo_event(request=request, action="created", instance=instance)
    return instance


def update_logo_metadata(*, serializer, request, instance):
    validate_department_access(user=request.user, company=instance.application.company)
    updated_instance = serializer.save(updated_by=request.user)
    logo_logger.info("logo metadata updated logo=%s", updated_instance.logo_code)
    _log_logo_event(request=request, action="updated", instance=updated_instance)
    return updated_instance


def replace_logo_file(*, instance, uploaded_file, request):
    validate_department_access(user=request.user, company=instance.application.company)
    metadata = validate_logo_upload(uploaded_file=uploaded_file, request=request, application=instance.application)
    old_file = instance.image_file

    instance.image_file = uploaded_file
    instance.original_file_name = metadata["original_file_name"]
    instance.file_size = metadata["file_size"]
    instance.mime_type = metadata["mime_type"]
    instance.width = metadata["width"]
    instance.height = metadata["height"]
    instance.updated_by = request.user
    instance.save()

    if old_file and old_file.name and old_file.name != instance.image_file.name:
        old_file.delete(save=False)

    logo_logger.info("logo file replaced logo=%s", instance.logo_code)
    _log_logo_event(request=request, action="replaced", instance=instance)
    return instance


def deactivate_logo_asset(*, instance, request):
    validate_department_access(user=request.user, company=instance.application.company)
    if not instance.is_active:
        return instance
    instance.is_active = False
    instance.updated_by = request.user
    instance.save(update_fields=["is_active", "updated_by", "updated_at"])
    logo_logger.info("logo deactivated logo=%s", instance.logo_code)
    _log_logo_event(request=request, action="deactivated", instance=instance)
    return instance
