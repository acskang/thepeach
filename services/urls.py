from django.urls import path

from .api_views import (
    RegisteredApplicationDeactivateAPIView,
    RegisteredApplicationDetailAPIView,
    RegisteredApplicationListCreateAPIView,
    RegisteredFeatureDeactivateAPIView,
    RegisteredFeatureDetailAPIView,
    RegisteredFeatureListCreateAPIView,
    RegisteredScreenDeactivateAPIView,
    RegisteredScreenDetailAPIView,
    RegisteredScreenListCreateAPIView,
    ServiceRegistryListAPIView,
)

app_name = "services"

urlpatterns = [
    path("", ServiceRegistryListAPIView.as_view(), name="service-list"),
    path("applications/", RegisteredApplicationListCreateAPIView.as_view(), name="application-list-create"),
    path("applications/<uuid:pk>/", RegisteredApplicationDetailAPIView.as_view(), name="application-detail"),
    path(
        "applications/<uuid:pk>/deactivate/",
        RegisteredApplicationDeactivateAPIView.as_view(),
        name="application-deactivate",
    ),
    path("screens/", RegisteredScreenListCreateAPIView.as_view(), name="screen-list-create"),
    path("screens/<uuid:pk>/", RegisteredScreenDetailAPIView.as_view(), name="screen-detail"),
    path("screens/<uuid:pk>/deactivate/", RegisteredScreenDeactivateAPIView.as_view(), name="screen-deactivate"),
    path("features/", RegisteredFeatureListCreateAPIView.as_view(), name="feature-list-create"),
    path("features/<uuid:pk>/", RegisteredFeatureDetailAPIView.as_view(), name="feature-detail"),
    path("features/<uuid:pk>/deactivate/", RegisteredFeatureDeactivateAPIView.as_view(), name="feature-deactivate"),
]
