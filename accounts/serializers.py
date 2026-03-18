from django.contrib.auth import get_user_model
from rest_framework import exceptions, serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Company, Department

User = get_user_model()


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("id", "name", "code", "is_active")
        read_only_fields = fields


class DepartmentSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = Department
        fields = ("id", "name", "code", "is_active", "company")
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    companies = serializers.SerializerMethodField()
    departments = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "display_name",
            "first_name",
            "last_name",
            "smartphone_number",
            "external_id",
            "companies",
            "departments",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_companies(self, obj):
        companies = Company.objects.filter(user_memberships__user=obj).distinct()
        return CompanySerializer(companies, many=True).data

    def get_departments(self, obj):
        departments = Department.objects.filter(user_memberships__user=obj).select_related("company").distinct()
        return DepartmentSerializer(departments, many=True).data


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    smartphone_number = serializers.CharField(
        required=False,
        allow_blank=False,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "display_name",
            "first_name",
            "last_name",
            "smartphone_number",
            "password",
        )
        read_only_fields = ("id",)

    def validate(self, attrs):
        if not attrs.get("full_name") and not attrs.get("display_name"):
            raise serializers.ValidationError({"full_name": "full_name is required."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        full_name = validated_data.get("full_name", "").strip()
        if full_name and not validated_data.get("display_name"):
            validated_data["display_name"] = full_name
        return User.objects.create_user(password=password, **validated_data)


class PlatformTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": "Invalid email or password.",
    }

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["full_name"] = user.full_name
        token["display_name"] = user.display_name
        token["company_ids"] = [str(company_id) for company_id in user.company_ids]
        token["department_ids"] = [str(department_id) for department_id in user.department_ids]
        return token

    def validate(self, attrs):
        if not attrs.get("email") or not attrs.get("password"):
            raise exceptions.ValidationError("Email and password are required.")
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self, **kwargs):
        refresh_token = self.validated_data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
