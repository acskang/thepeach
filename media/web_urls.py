from django.urls import path

from .web_views import LogoFormPageView, LogoListPageView, LogoUploadPageView

app_name = "media-web"

urlpatterns = [
    path("logos/", LogoListPageView.as_view(), name="logo-list-page"),
    path("logos/upload/", LogoUploadPageView.as_view(), name="logo-upload-page"),
    path("logos/<uuid:pk>/edit/", LogoFormPageView.as_view(), name="logo-edit-page"),
]
