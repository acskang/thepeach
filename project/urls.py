from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import include, path

from common.docs_views import DocsDetailView, DocsHubView
from common.views import HomeView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),
    path("docs/", DocsHubView.as_view(), name="docs-index"),
    path("docs/<slug:slug>/", DocsDetailView.as_view(), name="docs-detail"),
    path("auth/", include(("accounts.web_urls", "accounts-web"), namespace="accounts-web")),
    path("", include(("media.web_urls", "media-web"), namespace="media-web")),
    path("", include(("services.web_urls", "services-web"), namespace="services-web")),
    path("api/v1/", include("gateway.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
