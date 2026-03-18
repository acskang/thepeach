from rest_framework import generics, permissions, status

from common.responses import success_response

from .models import MediaAsset
from .serializers import MediaAssetSerializer
from .services import (
    create_media_asset,
    delete_media_asset,
    get_media_asset_queryset,
    update_media_asset,
)


class MediaAssetListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MediaAssetSerializer

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        asset_type = self.request.query_params.get("asset_type")
        reusable_only = self.request.query_params.get("reusable")
        return get_media_asset_queryset(
            user=self.request.user,
            asset_type=asset_type,
            reusable_only=reusable_only in {"1", "true", "yes"},
        )

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return success_response(data=response.data, status_code=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        create_media_asset(serializer=serializer, user=self.request.user)


class MediaAssetRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MediaAssetSerializer
    lookup_field = "slug"

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return get_media_asset_queryset(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return success_response(data=response.data, status_code=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return success_response(data=response.data, status_code=response.status_code)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_media_asset(user=request.user, instance=instance)
        return success_response(data={"deleted": True}, status_code=status.HTTP_200_OK)

    def perform_update(self, serializer):
        update_media_asset(serializer=serializer, user=self.request.user, instance=self.get_object())


class VideoAssetListAPIView(generics.ListAPIView):
    serializer_class = MediaAssetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_media_asset_queryset(
            user=self.request.user,
            asset_type=MediaAsset.TYPE_VIDEO,
        )
