from django.urls import path

from .logo_views import (
    PlatformLogoAssetByApplicationAPIView,
    PlatformLogoAssetDeactivateAPIView,
    PlatformLogoAssetDetailAPIView,
    PlatformLogoAssetListCreateAPIView,
    PlatformLogoAssetReplaceAPIView,
)
from .views import (
    MediaAssetListCreateAPIView,
    MediaAssetRetrieveUpdateDestroyAPIView,
    VideoAssetListAPIView,
)

app_name = "media"

urlpatterns = [
    path("", MediaAssetListCreateAPIView.as_view(), name="asset-list"),
    path("logos/", PlatformLogoAssetListCreateAPIView.as_view(), name="platform-logo-list-create"),
    path("logos/by-application/<slug:app_code>/", PlatformLogoAssetByApplicationAPIView.as_view(), name="platform-logo-by-application"),
    path("logos/<uuid:pk>/", PlatformLogoAssetDetailAPIView.as_view(), name="platform-logo-detail"),
    path("logos/<uuid:pk>/deactivate/", PlatformLogoAssetDeactivateAPIView.as_view(), name="platform-logo-deactivate"),
    path("logos/<uuid:pk>/replace/", PlatformLogoAssetReplaceAPIView.as_view(), name="platform-logo-replace"),
    path("videos/", VideoAssetListAPIView.as_view(), name="video-list"),
    path("<slug:slug>/", MediaAssetRetrieveUpdateDestroyAPIView.as_view(), name="asset-detail"),
]
