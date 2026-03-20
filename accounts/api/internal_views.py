from rest_framework import permissions
from rest_framework.views import APIView

from common.permissions import InternalOnlyAccessPermission
from common.responses import success_response

from accounts.services import build_internal_auth_manifest, get_auth_event_summary


class InternalAuthManifestView(APIView):
    permission_classes = [permissions.IsAuthenticated, InternalOnlyAccessPermission]

    def get(self, request, *args, **kwargs):
        return success_response(data=build_internal_auth_manifest())


class InternalAuthEventSummaryAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, InternalOnlyAccessPermission]

    def get(self, request, *args, **kwargs):
        return success_response(data=get_auth_event_summary())
