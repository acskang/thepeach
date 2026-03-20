from django.urls import path

from .web_views import AssetFormPageView, AssetListPageView, AssetUploadPageView

app_name = "media-web"

urlpatterns = [
    path("assets/", AssetListPageView.as_view(), name="asset-list-page"),
    path("assets/upload/", AssetUploadPageView.as_view(), name="asset-upload-page"),
    path("assets/<uuid:pk>/edit/", AssetFormPageView.as_view(), name="asset-edit-page"),
]
