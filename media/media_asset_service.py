import hashlib
import logging
from pathlib import Path

from django.conf import settings
from PIL import Image, UnidentifiedImageError
from rest_framework.exceptions import ValidationError

from logs.services import safe_create_system_log

from .models import SharedMediaAsset

asset_logger = logging.getLogger("media.asset")

ALLOWED_IMAGE_MIME_TYPES = {
    "PNG": "image/png",
    "JPEG": "image/jpeg",
}


def _serialize_asset_context(instance):
    return {
        "asset_id": str(instance.pk),
        "stored_file_name": instance.stored_file_name,
        "mime_type": instance.mime_type,
        "checksum_sha256": instance.checksum_sha256,
    }


def _log_asset_event(*, request, action, instance=None, detail=None, level="info"):
    safe_create_system_log(
        level=level,
        source="media.asset",
        message=f"shared media asset {action}",
        request_id=getattr(request, "request_id", ""),
        context={
            "action": action,
            "asset": _serialize_asset_context(instance) if instance else {},
            "user_id": str(getattr(request.user, "pk", "")),
            "detail": detail or {},
        },
    )


def _compute_checksum(uploaded_file):
    uploaded_file.seek(0)
    digest = hashlib.sha256()
    for chunk in uploaded_file.chunks():
        digest.update(chunk)
    uploaded_file.seek(0)
    return digest.hexdigest()


def get_shared_media_queryset(*, user, is_active=None, mime_type=None, title_query=None):
    queryset = SharedMediaAsset.objects.select_related("created_by")

    if user.is_authenticated:
        scoped = queryset
    else:
        scoped = queryset.none()

    if is_active is not None:
        scoped = scoped.filter(is_active=is_active)
    if mime_type:
        scoped = scoped.filter(mime_type=mime_type)
    if title_query:
        scoped = scoped.filter(title__icontains=title_query)

    return scoped


def validate_shared_media_upload(*, uploaded_file, request):
    asset_logger.info(
        "shared media upload attempt filename=%s size=%s",
        getattr(uploaded_file, "name", ""),
        getattr(uploaded_file, "size", 0),
    )

    if uploaded_file is None:
        _log_asset_event(request=request, action="validation_failed", detail={"reason": "missing_file"}, level="warning")
        raise ValidationError({"file": "file is required."})

    if uploaded_file.size <= 0:
        _log_asset_event(request=request, action="validation_failed", detail={"reason": "empty_file"}, level="warning")
        raise ValidationError({"file": "Uploaded file cannot be empty."})

    max_size = getattr(settings, "THEPEACH_MEDIA_MAX_UPLOAD_BYTES", 5 * 1024 * 1024)
    if uploaded_file.size > max_size:
        _log_asset_event(
            request=request,
            action="validation_failed",
            detail={"reason": "oversized_file", "size": uploaded_file.size},
            level="warning",
        )
        raise ValidationError({"file": f"Image files must be {max_size} bytes or smaller."})

    checksum_sha256 = _compute_checksum(uploaded_file)

    try:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        image.verify()
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        image_format = image.format
        width, height = image.size
    except (UnidentifiedImageError, OSError, ValueError):
        _log_asset_event(
            request=request,
            action="validation_failed",
            detail={"reason": "corrupted_or_invalid_image"},
            level="warning",
        )
        raise ValidationError({"file": "Uploaded file is not a valid image."})
    finally:
        uploaded_file.seek(0)

    if image_format not in ALLOWED_IMAGE_MIME_TYPES:
        _log_asset_event(
            request=request,
            action="validation_failed",
            detail={"reason": "unsupported_type", "format": image_format},
            level="warning",
        )
        raise ValidationError({"file": "Only PNG and JPEG image files are allowed."})

    return {
        "original_file_name": Path(getattr(uploaded_file, "name", "asset")).name,
        "file_size": uploaded_file.size,
        "mime_type": ALLOWED_IMAGE_MIME_TYPES[image_format],
        "width": width,
        "height": height,
        "checksum_sha256": checksum_sha256,
    }


def create_shared_media_asset(*, serializer, request):
    metadata = validate_shared_media_upload(uploaded_file=serializer.validated_data["file"], request=request)
    existing = SharedMediaAsset.objects.filter(
        checksum_sha256=metadata["checksum_sha256"],
        is_active=True,
    ).first()
    if existing:
        asset_logger.info("shared media deduplicated asset=%s", existing.pk)
        _log_asset_event(
            request=request,
            action="deduplicated",
            instance=existing,
            detail={"checksum_sha256": metadata["checksum_sha256"]},
        )
        return existing, False

    instance = serializer.save(
        created_by=request.user if request.user.is_authenticated else None,
        media_kind=SharedMediaAsset.KIND_IMAGE,
        **metadata,
    )
    instance.stored_file_name = Path(instance.file.name).name
    instance.save(update_fields=["stored_file_name", "updated_at"])

    asset_logger.info("shared media upload success asset=%s", instance.pk)
    _log_asset_event(request=request, action="created", instance=instance)
    return instance, True


def update_shared_media_asset(*, serializer, request):
    instance = serializer.save()
    asset_logger.info("shared media metadata updated asset=%s", instance.pk)
    _log_asset_event(request=request, action="updated", instance=instance)
    return instance


def replace_shared_media_file(*, instance, uploaded_file, request):
    metadata = validate_shared_media_upload(uploaded_file=uploaded_file, request=request)
    duplicate = (
        SharedMediaAsset.objects.filter(checksum_sha256=metadata["checksum_sha256"], is_active=True)
        .exclude(pk=instance.pk)
        .first()
    )
    if duplicate:
        _log_asset_event(
            request=request,
            action="replace_blocked_duplicate_checksum",
            instance=instance,
            detail={"duplicate_asset_id": str(duplicate.pk)},
            level="warning",
        )
        raise ValidationError({"file": "An active shared asset with the same checksum already exists."})

    old_file = instance.file
    instance.file = uploaded_file
    instance.original_file_name = metadata["original_file_name"]
    instance.file_size = metadata["file_size"]
    instance.mime_type = metadata["mime_type"]
    instance.width = metadata["width"]
    instance.height = metadata["height"]
    instance.checksum_sha256 = metadata["checksum_sha256"]
    instance.save()

    instance.stored_file_name = Path(instance.file.name).name
    instance.save(update_fields=["stored_file_name", "updated_at"])

    if old_file and old_file.name and old_file.name != instance.file.name:
        old_file.delete(save=False)

    asset_logger.info("shared media file replaced asset=%s", instance.pk)
    _log_asset_event(request=request, action="replaced", instance=instance)
    return instance


def deactivate_shared_media_asset(*, instance, request):
    if not instance.is_active:
        return instance
    instance.is_active = False
    instance.save(update_fields=["is_active", "updated_at"])
    asset_logger.info("shared media deactivated asset=%s", instance.pk)
    _log_asset_event(request=request, action="deactivated", instance=instance)
    return instance
