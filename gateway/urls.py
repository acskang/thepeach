from django.urls import include, path

from common.docs_views import DocsDetailAPIView, DocsIndexAPIView
from common.views import PlatformHealthView

from gateway.api.internal_views import (
    GatewayRouteCatalogView,
    GatewayRouteResolveView,
    GatewayToolApplicationsView,
    InternalGatewayManifestView,
)
from gateway.api.public_views import (
    ApiRootView,
    GatewayApplicationsIntegrationView,
    GatewayManifestView,
)

app_name = "gateway"

urlpatterns = [
    path("", ApiRootView.as_view(), name="api_root"),
    path("health/", PlatformHealthView.as_view(), name="health"),
    path("gateway/", GatewayManifestView.as_view(), name="gateway_manifest"),
    path("gateway/health/", PlatformHealthView.as_view(), name="gateway_health"),
    path(
        "gateway/integrations/applications/",
        GatewayApplicationsIntegrationView.as_view(),
        name="gateway_integrations_applications",
    ),
    path("gateway/internal/", InternalGatewayManifestView.as_view(), name="gateway_internal_manifest"),
    path("gateway/internal/routes/", GatewayRouteCatalogView.as_view(), name="gateway_internal_routes"),
    path("gateway/internal/resolve/", GatewayRouteResolveView.as_view(), name="gateway_internal_resolve"),
    path("gateway/tools/applications/", GatewayToolApplicationsView.as_view(), name="gateway_tools_applications"),
    path("gateway/routes/", GatewayRouteCatalogView.as_view(), name="gateway_routes"),
    path("gateway/resolve/", GatewayRouteResolveView.as_view(), name="gateway_resolve"),
    path("docs/", DocsIndexAPIView.as_view(), name="docs_index_api"),
    path("docs/<slug:slug>/", DocsDetailAPIView.as_view(), name="docs_detail_api"),
    path("auth/", include(("accounts.urls", "auth"), namespace="auth")),
    path("media/", include("media.urls")),
    path("services/", include("services.urls")),
]
