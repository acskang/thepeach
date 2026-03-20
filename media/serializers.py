from rest_framework import serializers

from accounts.models import Company
from common.tenancy import validate_company_membership

from .models import MediaAsset, SharedMediaAsset


class MediaAssetSerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()
    company_id = serializers.UUIDField(write_only=True, required=False)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = MediaAsset
        fields = (
            "id",
            "company",
            "company_id",
            "title",
            "slug",
            "asset_type",
            "source_type",
            "file",
            "file_url",
            "source_url",
            "embed_url",
            "alt_text",
            "description",
            "is_public",
            "is_reusable",
            "metadata",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "company", "file_url", "created_at", "updated_at")

    def get_file_url(self, obj):
        request = self.context.get("request")
        if not obj.file:
            return ""
        if request is None:
            return obj.file.url
        return request.build_absolute_uri(obj.file.url)

    def get_company(self, obj):
        return {
            "id": str(obj.company_id),
            "name": obj.company.name,
            "code": obj.company.code,
            "is_active": obj.company.is_active,
        }

    def validate(self, attrs):
        request = self.context.get("request")
        company_id = attrs.pop("company_id", None)

        if self.instance is None:
            if company_id is None:
                raise serializers.ValidationError({"company_id": "company_id is required."})
            company = Company.objects.filter(id=company_id, is_active=True).first()
            if company is None:
                raise serializers.ValidationError({"company_id": "Selected company does not exist."})
            validate_company_membership(user=request.user, company=company)
            attrs["company"] = company

        source_type = attrs.get("source_type", getattr(self.instance, "source_type", MediaAsset.SOURCE_URL))
        file_value = attrs.get("file", getattr(self.instance, "file", None))
        source_url = attrs.get("source_url", getattr(self.instance, "source_url", ""))
        embed_url = attrs.get("embed_url", getattr(self.instance, "embed_url", ""))

        if source_type == MediaAsset.SOURCE_FILE and not file_value:
            raise serializers.ValidationError({"file": "File source assets require an uploaded file."})
        if source_type == MediaAsset.SOURCE_URL and not source_url:
            raise serializers.ValidationError({"source_url": "URL source assets require source_url."})
        if source_type == MediaAsset.SOURCE_EMBED and not embed_url:
            raise serializers.ValidationError({"embed_url": "Embed source assets require embed_url."})

        asset_type = attrs.get("asset_type", getattr(self.instance, "asset_type", None))
        if asset_type == MediaAsset.TYPE_VIDEO and source_type not in {MediaAsset.SOURCE_URL, MediaAsset.SOURCE_EMBED}:
            raise serializers.ValidationError({"source_type": "Video assets must use url or embed sources."})

        return attrs


class SharedMediaAssetReadSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = SharedMediaAsset
        fields = (
            "id",
            "title",
            "original_file_name",
            "stored_file_name",
            "file_url",
            "file_size",
            "mime_type",
            "width",
            "height",
            "checksum_sha256",
            "alt_text",
            "description",
            "media_kind",
            "is_active",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_file_url(self, obj):
        request = self.context.get("request")
        if not obj.file:
            return ""
        if request is None:
            return obj.file.url
        return request.build_absolute_uri(obj.file.url)

    def _serialize_user(self, user):
        if user is None:
            return None
        return {
            "id": str(user.pk),
            "email": user.email,
            "full_name": user.full_name,
        }

    def get_created_by(self, obj):
        return self._serialize_user(obj.created_by)


class SharedMediaAssetCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)

    class Meta:
        model = SharedMediaAsset
        fields = (
            "id",
            "file",
            "title",
            "alt_text",
            "description",
        )
        read_only_fields = ("id",)

    def validate_alt_text(self, value):
        if len(value) > 255:
            raise serializers.ValidationError("alt_text must be 255 characters or fewer.")
        return value


class SharedMediaAssetUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedMediaAsset
        fields = ("title", "alt_text", "description", "is_active")

    def validate_alt_text(self, value):
        if len(value) > 255:
            raise serializers.ValidationError("alt_text must be 255 characters or fewer.")
        return value


class SharedMediaAssetReplaceSerializer(serializers.Serializer):
    file = serializers.FileField()
