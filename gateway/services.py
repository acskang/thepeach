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
    },
    "health": {
        "path": "/api/v1/health/",
        "methods": ["GET"],
        "auth_required": False,
        "kind": "platform",
        "mcp_exposed": True,
        "description": "Platform health probe endpoint.",
    },
    "media": {
        "path": "/api/v1/media/",
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE"],
        "auth_required": True,
        "kind": "platform",
        "mcp_exposed": True,
        "description": "Company-scoped media asset registry.",
    },
    "services": {
        "path": "/api/v1/services/",
        "methods": ["GET"],
        "auth_required": True,
        "kind": "integration",
        "mcp_exposed": True,
        "description": "Service registry and integration entry catalog.",
    },
    "gateway": {
        "path": "/api/v1/gateway/",
        "methods": ["GET", "POST"],
        "auth_required": False,
        "kind": "integration",
        "mcp_exposed": True,
        "description": "Gateway discovery, route catalog, and route resolution API.",
    },
}


def build_gateway_manifest():
    return {
        "name": "ThePeach API Gateway",
        "version": "v1",
        "auth_namespace": {
            "canonical": "/api/v1/auth/",
            "legacy_aliases": [],
        },
        "role": [
            "unified-api-entry",
            "routing-layer",
            "integration-layer",
            "logging-aware-edge",
            "mcp-compatible-interface",
        ],
        "modules": STATIC_GATEWAY_MODULES,
        "integrations": {
            "applications": "/api/v1/gateway/integrations/applications/",
            "health": "/api/v1/gateway/health/",
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


def build_registered_application_catalog(*, user):
    queryset = company_scoped_queryset(
        RegisteredApplication.objects.filter(is_active=True).select_related("company"),
        user,
    )
    return RegisteredApplicationIntegrationSerializer(queryset, many=True).data


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
