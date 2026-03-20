from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.views import APIView

from common.responses import success_response

from .media_asset_service import (
    create_shared_media_asset,
    deactivate_shared_media_asset,
    get_shared_media_queryset,
    replace_shared_media_file,
    update_shared_media_asset,
)
from .models import SharedMediaAsset
from .serializers import (
    SharedMediaAssetCreateSerializer,
    SharedMediaAssetReadSerializer,
    SharedMediaAssetReplaceSerializer,
    SharedMediaAssetUpdateSerializer,
)


class SharedMediaAssetListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SharedMediaAssetCreateSerializer
        return SharedMediaAssetReadSerializer

    def get_queryset(self):
        is_active_param = self.request.query_params.get("is_active")
        is_active = None
        if is_active_param is not None:
            is_active = is_active_param.lower() in {"1", "true", "yes", "on"}
        return get_shared_media_queryset(
            user=self.request.user,
            is_active=is_active,
            mime_type=self.request.query_params.get("mime_type"),
            title_query=self.request.query_params.get("title"),
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance, created = create_shared_media_asset(serializer=serializer, request=request)
        response_serializer = SharedMediaAssetReadSerializer(instance, context=self.get_serializer_context())
        payload = dict(response_serializer.data)
        payload["deduplicated"] = not created
        return success_response(
            data=payload,
            status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class SharedMediaAssetDetailAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = SharedMediaAsset.objects.select_related("created_by")

    def get_serializer_class(self):
        if self.request.method in {"PATCH", "PUT"}:
            return SharedMediaAssetUpdateSerializer
        return SharedMediaAssetReadSerializer

    def get_queryset(self):
        return get_shared_media_queryset(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response(data=serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = update_shared_media_asset(serializer=serializer, request=request)
        response_serializer = SharedMediaAssetReadSerializer(instance, context=self.get_serializer_context())
        return success_response(data=response_serializer.data)


class SharedMediaAssetDeactivateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        instance = get_shared_media_queryset(user=request.user).get(pk=pk)
        instance = deactivate_shared_media_asset(instance=instance, request=request)
        return success_response(data={"deactivated": True, "id": str(instance.pk)})


class SharedMediaAssetReplaceAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk, *args, **kwargs):
        instance = get_shared_media_queryset(user=request.user).get(pk=pk)
        serializer = SharedMediaAssetReplaceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = replace_shared_media_file(
            instance=instance,
            uploaded_file=serializer.validated_data["file"],
            request=request,
        )
        response_serializer = SharedMediaAssetReadSerializer(instance, context={"request": request})
        return success_response(data=response_serializer.data)


class SharedMediaAssetByChecksumAPIView(generics.RetrieveAPIView):
    serializer_class = SharedMediaAssetReadSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "checksum"

    def get_queryset(self):
        return get_shared_media_queryset(user=self.request.user, is_active=True)

    def get_object(self):
        return self.get_queryset().get(checksum_sha256=self.kwargs["checksum"])

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response(data=serializer.data)
