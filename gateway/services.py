from django.conf import settings

from common.tenancy import company_scoped_queryset
from logs.services import safe_create_system_log
from services.models import RegisteredApplication, ServiceRegistry
from services.serializers import RegisteredApplicationIntegrationSerializer


STATIC_GATEWAY_MODULES = {
    "auth": {
        "path": "/api/v1/auth/",
        "methods": ["GET", "POST"],
        "auth_required": False,
        "kind": "platform",
        "mcp_exposed": True,
        "description": "Central authentication surface for JWT and future SSO extensions.",
        "zone": "public",
    },
    "health": {
        "path": "/api/v1/health/",
        "methods": ["GET"],
        "auth_required": False,
        "kind": "platform",
        "mcp_exposed": True,
        "description": "Platform health probe endpoint.",
        "zone": "public",
    },
    "media": {
        "path": "/api/v1/media/",
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE"],
        "auth_required": True,
        "kind": "platform",
        "mcp_exposed": True,
        "description": "Company-scoped media asset registry.",
        "zone": "public",
    },
    "services": {
        "path": "/api/v1/services/",
        "methods": ["GET"],
        "auth_required": True,
        "kind": "integration",
        "mcp_exposed": True,
        "description": "Service registry and integration entry catalog.",
        "zone": "public",
    },
    "gateway": {
        "path": "/api/v1/gateway/",
        "methods": ["GET"],
        "auth_required": False,
        "kind": "integration",
        "mcp_exposed": True,
        "description": "Gateway discovery, route catalog, and route resolution API.",
        "zone": "public",
    },
}

INTERNAL_GATEWAY_ENDPOINTS = {
    "manifest": {
        "path": "/api/v1/gateway/internal/",
        "methods": ["GET"],
        "auth_required": True,
        "kind": "operations",
        "mcp_exposed": False,
    },
    "route_catalog": {
        "path": "/api/v1/gateway/internal/routes/",
        "methods": ["GET"],
        "auth_required": True,
        "kind": "operations",
        "mcp_exposed": False,
    },
    "route_resolve": {
        "path": "/api/v1/gateway/internal/resolve/",
        "methods": ["POST"],
        "auth_required": True,
        "kind": "operations",
        "mcp_exposed": False,
    },
    "tools_applications": {
        "path": "/api/v1/gateway/tools/applications/",
        "methods": ["GET"],
        "auth_required": True,
        "kind": "operations",
        "mcp_exposed": False,
    },
}


def build_gateway_manifest(*, zone="public"):
    return {
        "name": "ThePeach API Gateway",
        "version": "v1",
        "zone": zone,
        "public_domain": settings.THEPEACH_PUBLIC_DOMAIN,
        "ops_domains": [
            settings.THEPEACH_OPS_DOMAIN,
            settings.THEPEACH_INTERNAL_AUTH_DOMAIN,
        ],
        "auth_namespace": {
            "canonical": "/api/v1/auth/",
            "internal": "/api/v1/auth/internal/",
            "legacy_aliases": [],
        },
        "role": [
            "unified-api-entry",
            "routing-layer",
            "integration-layer",
            "logging-aware-edge",
            "mcp-compatible-interface",
        ],
        "modules": STATIC_GATEWAY_MODULES if zone == "public" else {**STATIC_GATEWAY_MODULES, "internal": INTERNAL_GATEWAY_ENDPOINTS},
        "public_endpoints": {
            "manifest": "/api/v1/gateway/",
            "applications": "/api/v1/gateway/integrations/applications/",
            "health": "/api/v1/gateway/health/",
        },
        "internal_endpoints": {
            "manifest": "/api/v1/gateway/internal/",
            "route_catalog": "/api/v1/gateway/internal/routes/",
            "route_resolve": "/api/v1/gateway/internal/resolve/",
            "tools_applications": "/api/v1/gateway/tools/applications/",
            "legacy_routes_alias": "/api/v1/gateway/routes/",
            "legacy_resolve_alias": "/api/v1/gateway/resolve/",
        },
        "internal_access_policy": {
            "allowed_hosts": list(settings.THEPEACH_INTERNAL_ALLOWED_HOSTS),
            "required_headers": list(settings.THEPEACH_INTERNAL_REQUIRED_HEADERS),
        },
        "response_contract": {
            "success": True,
            "data": {},
            "error": None,
        },
    }


def build_gateway_route_catalog(user):
    catalog = []

    for code, module in STATIC_GATEWAY_MODULES.items():
        if module["auth_required"] and not getattr(user, "is_authenticated", False):
            continue
        catalog.append(
            {
                "code": code,
                **module,
            }
        )

    if getattr(user, "is_authenticated", False):
        queryset = company_scoped_queryset(
            ServiceRegistry.objects.filter(is_active=True).select_related("company"),
            user,
        )
        for service in queryset:
            catalog.append(
                {
                    "code": f"service:{service.code}",
                    "path": service.base_path,
                    "methods": ["ANY"],
                    "auth_required": service.requires_authentication,
                    "kind": "service",
                    "mcp_exposed": True,
                    "description": service.description or service.name,
                    "company": {
                        "id": str(service.company_id),
                        "name": service.company.name,
                        "code": service.company.code,
                    },
                    "service": {
                        "name": service.name,
                        "code": service.code,
                        "upstream_url": service.upstream_url,
                    },
                }
            )

    return catalog


def build_registered_application_catalog(*, user, include_internal_metadata=False, request_id=""):
    queryset = company_scoped_queryset(
        RegisteredApplication.objects.filter(is_active=True).select_related("company"),
        user,
    )
    payload = RegisteredApplicationIntegrationSerializer(queryset, many=True).data
    if include_internal_metadata:
        safe_create_system_log(
            level="info",
            source="gateway.tools.applications",
            message="Gateway internal application tool called.",
            request_id=request_id,
            context={
                "application_count": len(payload),
                "user_id": str(getattr(user, "pk", "")),
            },
        )
    return payload


def resolve_gateway_target(*, user, method, module=None, service_code=None, path=None):
    if module and module in STATIC_GATEWAY_MODULES:
        target = STATIC_GATEWAY_MODULES[module]
        return {
            "resolved": True,
            "target_type": "platform",
            "module": module,
            "method": method,
            "path": target["path"],
            "auth_required": target["auth_required"],
            "mcp_exposed": target["mcp_exposed"],
        }

    queryset = company_scoped_queryset(
        ServiceRegistry.objects.filter(is_active=True).select_related("company"),
        user,
    )

    service = None
    if service_code:
        service = queryset.filter(code=service_code).first()
    elif path:
        service = queryset.filter(base_path=path).first()

    if service is None:
        return {
            "resolved": False,
            "target_type": "unknown",
            "method": method,
            "path": path or "",
            "service_code": service_code or "",
        }

    return {
        "resolved": True,
        "target_type": "service",
        "method": method,
        "path": service.base_path,
        "auth_required": service.requires_authentication,
        "mcp_exposed": True,
        "service": {
            "name": service.name,
            "code": service.code,
            "upstream_url": service.upstream_url,
            "company": {
                "id": str(service.company_id),
                "name": service.company.name,
                "code": service.company.code,
            },
        },
    }


def resolve_gateway_request(*, user, request_id, validated_data):
    resolved_target = resolve_gateway_target(
        user=user,
        **validated_data,
    )

    safe_create_system_log(
        level="info",
        source="gateway.resolve",
        message="Gateway target resolution requested.",
        request_id=request_id,
        context=resolved_target,
    )

    return resolved_target
