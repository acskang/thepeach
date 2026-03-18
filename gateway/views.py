from rest_framework import permissions
from rest_framework.views import APIView

from common.responses import error_response, success_response

from .serializers import GatewayRouteResolveSerializer
from .services import (
    build_gateway_manifest,
    build_registered_application_catalog,
    build_gateway_route_catalog,
    resolve_gateway_request,
)


class ApiRootView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        manifest = build_gateway_manifest()
        return success_response(data=manifest)


class GatewayManifestView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return success_response(data=build_gateway_manifest())


class GatewayApplicationsIntegrationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return success_response(
            data={
                "applications": build_registered_application_catalog(user=request.user),
            }
        )


class GatewayRouteCatalogView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return success_response(
            data={
                "routes": build_gateway_route_catalog(request.user),
            }
        )


class GatewayRouteResolveView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = GatewayRouteResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        resolved_target = resolve_gateway_request(
            user=request.user,
            request_id=getattr(request, "request_id", ""),
            validated_data=serializer.validated_data,
        )

        if not resolved_target["resolved"]:
            return error_response(
                message="Gateway target was not found.",
                code="route_not_found",
                details=resolved_target,
                status_code=404,
            )

        return success_response(data=resolved_target)
