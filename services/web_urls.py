from django.urls import path

from .web_views import ApplicationRegistryFormPageView, ApplicationRegistryListPageView

app_name = "services-web"

urlpatterns = [
    path("applications/", ApplicationRegistryListPageView.as_view(), name="application-list-page"),
    path("applications/new/", ApplicationRegistryFormPageView.as_view(), name="application-create-page"),
    path("applications/<uuid:pk>/edit/", ApplicationRegistryFormPageView.as_view(), name="application-edit-page"),
]
