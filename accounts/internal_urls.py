from django.urls import path

from accounts.api.internal_views import InternalAuthEventSummaryAPIView, InternalAuthManifestView

urlpatterns = [
    path("", InternalAuthManifestView.as_view(), name="internal_root"),
    path("events/summary/", InternalAuthEventSummaryAPIView.as_view(), name="internal_events_summary"),
]
