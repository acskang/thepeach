from django.contrib import admin
from django.urls import include, path

from common.views import HomeView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),
    path("auth/", include(("accounts.web_urls", "accounts-web"), namespace="accounts-web")),
    path("", include(("media.web_urls", "media-web"), namespace="media-web")),
    path("", include(("services.web_urls", "services-web"), namespace="services-web")),
    path("api/v1/", include("gateway.urls")),
]
