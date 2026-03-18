from django.urls import include, path

from common.views import PlatformHealthView

from .views import (
    ApiRootView,
    GatewayApplicationsIntegrationView,
    GatewayManifestView,
    GatewayRouteCatalogView,
    GatewayRouteResolveView,
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
    path("gateway/routes/", GatewayRouteCatalogView.as_view(), name="gateway_routes"),
    path("gateway/resolve/", GatewayRouteResolveView.as_view(), name="gateway_resolve"),
    path("auth/", include(("accounts.urls", "auth"), namespace="auth")),
    path("media/", include("media.urls")),
    path("services/", include("services.urls")),
]
