from rest_framework import serializers

from accounts.models import Company
from common.tenancy import validate_company_membership

from .models import RegisteredApplication, RegisteredFeature, RegisteredScreen, ServiceRegistry


class CompanyReferenceMixin:
    def serialize_company(self, company):
        return {
            "id": str(company.id),
            "name": company.name,
            "code": company.code,
            "is_active": company.is_active,
        }


class ServiceRegistrySerializer(serializers.ModelSerializer, CompanyReferenceMixin):
    company = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRegistry
        fields = (
            "id",
            "company",
            "name",
            "code",
            "description",
            "base_path",
            "upstream_url",
            "is_active",
            "requires_authentication",
            "metadata",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_company(self, obj):
        return self.serialize_company(obj.company)


class RegisteredApplicationSerializer(serializers.ModelSerializer, CompanyReferenceMixin):
    company = serializers.SerializerMethodField(read_only=True)
    company_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = RegisteredApplication
        fields = (
            "id",
            "company",
            "company_id",
            "app_code",
            "app_name",
            "app_description",
            "app_domain",
            "app_base_url",
            "is_active",
            "requires_sso",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "company", "created_at", "updated_at")

    def get_company(self, obj):
        return self.serialize_company(obj.company)

    def validate_company_id(self, value):
        company = Company.objects.filter(id=value, is_active=True).first()
        if company is None:
            raise serializers.ValidationError("Selected company does not exist.")
        validate_company_membership(user=self.context["request"].user, company=company)
        return value

    def validate(self, attrs):
        company_id = attrs.pop("company_id", None)
        if self.instance is not None and company_id and company_id != self.instance.company_id:
            raise serializers.ValidationError({"company_id": "Application company cannot be changed."})
        if self.instance is None:
            if company_id is None:
                raise serializers.ValidationError({"company_id": "company_id is required."})
            attrs["company"] = Company.objects.get(id=company_id)
        return attrs


class RegisteredApplicationIntegrationSerializer(serializers.ModelSerializer, CompanyReferenceMixin):
    company = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RegisteredApplication
        fields = (
            "id",
            "company",
            "app_code",
            "app_name",
            "app_description",
            "app_domain",
            "app_base_url",
            "requires_sso",
            "is_active",
        )
        read_only_fields = fields

    def get_company(self, obj):
        return self.serialize_company(obj.company)


class RegisteredScreenSerializer(serializers.ModelSerializer):
    application_id = serializers.UUIDField(write_only=True)
    application = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RegisteredScreen
        fields = (
            "id",
            "application",
            "application_id",
            "screen_code",
            "screen_name",
            "route_path",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "application", "created_at", "updated_at")

    def get_application(self, obj):
        return {
            "id": str(obj.application_id),
            "app_code": obj.application.app_code,
            "app_name": obj.application.app_name,
            "company_id": str(obj.application.company_id),
        }

    def validate(self, attrs):
        application_id = attrs.pop("application_id", None)
        request = self.context["request"]

        if self.instance is None:
            if application_id is None:
                raise serializers.ValidationError({"application_id": "application_id is required."})
            application = (
                RegisteredApplication.objects.select_related("company")
                .filter(id=application_id)
                .first()
            )
            if application is None:
                raise serializers.ValidationError({"application_id": "Selected application does not exist."})
            validate_company_membership(user=request.user, company=application.company)
            if attrs.get("is_active", True) and not application.is_active:
                raise serializers.ValidationError(
                    {"application_id": "Inactive applications cannot receive active screens."}
                )
            attrs["application"] = application

        return attrs


class RegisteredFeatureSerializer(serializers.ModelSerializer):
    application_id = serializers.UUIDField(write_only=True)
    screen_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    application = serializers.SerializerMethodField(read_only=True)
    screen = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RegisteredFeature
        fields = (
            "id",
            "application",
            "application_id",
            "screen",
            "screen_id",
            "feature_code",
            "feature_name",
            "feature_type",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "application", "screen", "created_at", "updated_at")

    def get_application(self, obj):
        return {
            "id": str(obj.application_id),
            "app_code": obj.application.app_code,
            "app_name": obj.application.app_name,
            "company_id": str(obj.application.company_id),
        }

    def get_screen(self, obj):
        if obj.screen_id is None:
            return None
        return {
            "id": str(obj.screen_id),
            "screen_code": obj.screen.screen_code,
            "screen_name": obj.screen.screen_name,
        }

    def validate(self, attrs):
        application_id = attrs.pop("application_id", None)
        screen_id = attrs.pop("screen_id", None)
        request = self.context["request"]

        if self.instance is None:
            if application_id is None:
                raise serializers.ValidationError({"application_id": "application_id is required."})
            application = (
                RegisteredApplication.objects.select_related("company")
                .filter(id=application_id)
                .first()
            )
            if application is None:
                raise serializers.ValidationError({"application_id": "Selected application does not exist."})
            validate_company_membership(user=request.user, company=application.company)
            if attrs.get("is_active", True) and not application.is_active:
                raise serializers.ValidationError(
                    {"application_id": "Inactive applications cannot receive active features."}
                )
            attrs["application"] = application

            if screen_id:
                screen = RegisteredScreen.objects.filter(id=screen_id, application=application).first()
                if screen is None:
                    raise serializers.ValidationError({"screen_id": "Selected screen does not belong to this application."})
                attrs["screen"] = screen
        return attrs
