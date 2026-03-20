from rest_framework import permissions
from rest_framework.views import APIView

from common.responses import success_response

from gateway.services import build_gateway_manifest, build_registered_application_catalog


class ApiRootView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return success_response(data=build_gateway_manifest(zone="public"))


class GatewayManifestView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return success_response(data=build_gateway_manifest(zone="public"))


class GatewayApplicationsIntegrationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return success_response(
            data={
                "applications": build_registered_application_catalog(
                    user=request.user,
                    include_internal_metadata=False,
                    request_id=getattr(request, "request_id", ""),
                ),
            }
        )
