from django.urls import path

from .asset_views import (
    SharedMediaAssetByChecksumAPIView,
    SharedMediaAssetDeactivateAPIView,
    SharedMediaAssetDetailAPIView,
    SharedMediaAssetListCreateAPIView,
    SharedMediaAssetReplaceAPIView,
)
from .views import (
    MediaAssetListCreateAPIView,
    MediaAssetRetrieveUpdateDestroyAPIView,
    VideoAssetListAPIView,
)

app_name = "media"

urlpatterns = [
    path("", MediaAssetListCreateAPIView.as_view(), name="asset-list"),
    path("assets/", SharedMediaAssetListCreateAPIView.as_view(), name="shared-asset-list-create"),
    path("assets/by-checksum/<str:checksum>/", SharedMediaAssetByChecksumAPIView.as_view(), name="shared-asset-by-checksum"),
    path("assets/<uuid:pk>/", SharedMediaAssetDetailAPIView.as_view(), name="shared-asset-detail"),
    path("assets/<uuid:pk>/deactivate/", SharedMediaAssetDeactivateAPIView.as_view(), name="shared-asset-deactivate"),
    path("assets/<uuid:pk>/replace/", SharedMediaAssetReplaceAPIView.as_view(), name="shared-asset-replace"),
    path("videos/", VideoAssetListAPIView.as_view(), name="video-list"),
    path("<slug:slug>/", MediaAssetRetrieveUpdateDestroyAPIView.as_view(), name="asset-detail"),
]
