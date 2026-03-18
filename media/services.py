from common.tenancy import company_scoped_queryset, validate_department_access

from .models import MediaAsset


def get_media_asset_queryset(*, user, asset_type=None, reusable_only=False):
    queryset = company_scoped_queryset(
        MediaAsset.objects.select_related("company"),
        user,
    )

    if asset_type:
        queryset = queryset.filter(asset_type=asset_type)
    if reusable_only:
        queryset = queryset.filter(is_reusable=True)

    return queryset


def create_media_asset(*, serializer, user):
    company = serializer.validated_data["company"]
    validate_department_access(user=user, company=company)
    return serializer.save()


def update_media_asset(*, serializer, user, instance):
    validate_department_access(user=user, company=instance.company)
    return serializer.save()


def delete_media_asset(*, user, instance):
    validate_department_access(user=user, company=instance.company)
    instance.delete()
