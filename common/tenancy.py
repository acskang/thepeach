from rest_framework.exceptions import PermissionDenied


def company_scoped_queryset(queryset, user):
    if user.is_superuser:
        return queryset
    if not user.is_authenticated:
        return queryset.none()
    return queryset.filter(company_id__in=user.company_ids)


def validate_company_membership(*, user, company):
    if user.is_superuser:
        return
    if not user.is_authenticated or not user.belongs_to_company(company.id):
        raise PermissionDenied("You do not have access to this company.")


def validate_department_access(*, user, company):
    if user.is_superuser:
        return
    if not user.is_authenticated or not user.has_department_access(company.id):
        raise PermissionDenied("Department membership is required for this company.")
