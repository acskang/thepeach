from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.views import APIView

from common.responses import success_response

from .logo_service import create_logo_asset, deactivate_logo_asset, get_logo_queryset, replace_logo_file, update_logo_metadata
from .models import PlatformLogoAsset
from .serializers import (
    PlatformLogoAssetCreateSerializer,
    PlatformLogoAssetReadSerializer,
    PlatformLogoAssetReplaceSerializer,
    PlatformLogoAssetUpdateSerializer,
)


class PlatformLogoAssetListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PlatformLogoAssetCreateSerializer
        return PlatformLogoAssetReadSerializer

    def get_queryset(self):
        is_active_param = self.request.query_params.get("is_active")
        is_active = None
        if is_active_param is not None:
            is_active = is_active_param.lower() in {"1", "true", "yes", "on"}

        return get_logo_queryset(
            user=self.request.user,
            application_code=self.request.query_params.get("application"),
            usage_type=self.request.query_params.get("usage_type"),
            is_active=is_active,
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = create_logo_asset(serializer=serializer, request=request)
        response_serializer = PlatformLogoAssetReadSerializer(instance, context=self.get_serializer_context())
        return success_response(data=response_serializer.data, status_code=status.HTTP_201_CREATED)


class PlatformLogoAssetDetailAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = PlatformLogoAsset.objects.select_related("application", "application__company", "created_by", "updated_by")

    def get_serializer_class(self):
        if self.request.method in {"PATCH", "PUT"}:
            return PlatformLogoAssetUpdateSerializer
        return PlatformLogoAssetReadSerializer

    def get_queryset(self):
        return get_logo_queryset(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = update_logo_metadata(serializer=serializer, request=request, instance=instance)
        response_serializer = PlatformLogoAssetReadSerializer(instance, context=self.get_serializer_context())
        return success_response(data=response_serializer.data)


class PlatformLogoAssetDeactivateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        instance = get_logo_queryset(user=request.user).get(pk=pk)
        deactivate_logo_asset(instance=instance, request=request)
        return success_response(data={"deactivated": True, "id": str(instance.pk)})


class PlatformLogoAssetReplaceAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk, *args, **kwargs):
        instance = get_logo_queryset(user=request.user).get(pk=pk)
        serializer = PlatformLogoAssetReplaceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = replace_logo_file(instance=instance, uploaded_file=serializer.validated_data["image_file"], request=request)
        response_serializer = PlatformLogoAssetReadSerializer(instance, context={"request": request})
        return success_response(data=response_serializer.data)


class PlatformLogoAssetByApplicationAPIView(generics.ListAPIView):
    serializer_class = PlatformLogoAssetReadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_logo_queryset(
            user=self.request.user,
            application_code=self.kwargs["app_code"],
            is_active=True,
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
