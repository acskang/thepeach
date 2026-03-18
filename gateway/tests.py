from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model

from accounts.models import Company, Department, UserCompanyMembership, UserDepartmentMembership
from gateway.serializers import GatewayRouteResolveSerializer
from services.models import RegisteredApplication, ServiceRegistry


class GatewayAPITestCase(APITestCase):
    def test_api_root_uses_standard_response_shape(self):
        response = self.client.get("/api/v1/", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), {"success", "data", "error"})
        self.assertTrue(response.data["success"])
        self.assertIn("auth", response.data["data"]["modules"])
        self.assertIn("gateway", response.data["data"]["modules"])

    def test_health_endpoint_returns_ok(self):
        response = self.client.get("/api/v1/health/", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["status"], "ok")

    def test_gateway_health_endpoint_returns_ok(self):
        response = self.client.get("/api/v1/gateway/health/", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["status"], "ok")

    def test_gateway_manifest_exposes_integration_role(self):
        response = self.client.get("/api/v1/gateway/", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("routing-layer", response.data["data"]["role"])
        self.assertIn("gateway", response.data["data"]["modules"])

    def test_gateway_route_catalog_includes_company_scoped_services(self):
        user_model = get_user_model()
        company = Company.objects.create(name="Gateway Alpha", code="gateway-alpha")
        department = Department.objects.create(company=company, name="Platform", code="platform")
        user = user_model.objects.create_user(
            email="gateway@example.com",
            password="StrongPass123",
            smartphone_number="+821088880010",
        )
        UserCompanyMembership.objects.create(user=user, company=company, role="member", is_default=True)
        UserDepartmentMembership.objects.create(user=user, department=department, role="member")
        ServiceRegistry.objects.create(
            company=company,
            name="Gateway Billing",
            code="gateway-billing",
            base_path="/services/gateway-billing/",
            upstream_url="https://billing.internal/api/",
            description="Billing integration",
        )

        self.client.force_authenticate(user=user)
        response = self.client.get("/api/v1/gateway/routes/", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        route_codes = {route["code"] for route in response.data["data"]["routes"]}
        self.assertIn("gateway", route_codes)
        self.assertIn("service:gateway-billing", route_codes)

    def test_gateway_resolve_returns_service_target(self):
        user_model = get_user_model()
        company = Company.objects.create(name="Gateway Beta", code="gateway-beta")
        department = Department.objects.create(company=company, name="Platform", code="platform")
        user = user_model.objects.create_user(
            email="resolver@example.com",
            password="StrongPass123",
            smartphone_number="+821088880011",
        )
        UserCompanyMembership.objects.create(user=user, company=company, role="member", is_default=True)
        UserDepartmentMembership.objects.create(user=user, department=department, role="member")
        ServiceRegistry.objects.create(
            company=company,
            name="Resolver Service",
            code="resolver-service",
            base_path="/services/resolver-service/",
            upstream_url="https://resolver.internal/api/",
        )

        self.client.force_authenticate(user=user)
        response = self.client.post(
            "/api/v1/gateway/resolve/",
            {
                "method": "GET",
                "service_code": "resolver-service",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["data"]["resolved"])
        self.assertEqual(response.data["data"]["target_type"], "service")
        self.assertEqual(response.data["data"]["service"]["code"], "resolver-service")

    def test_gateway_resolve_returns_404_for_unknown_target(self):
        response = self.client.post(
            "/api/v1/gateway/resolve/",
            {
                "method": "GET",
                "service_code": "missing-service",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "route_not_found")

    def test_gateway_resolver_accepts_all_manifest_platform_modules(self):
        for module in ["auth", "health", "media", "services", "gateway"]:
            serializer = GatewayRouteResolveSerializer(
                data={
                    "method": "GET",
                    "module": module,
                }
            )
            self.assertTrue(serializer.is_valid(), msg=f"module={module} should be accepted")

    def test_gateway_resolve_accepts_services_root_module(self):
        response = self.client.post(
            "/api/v1/gateway/resolve/",
            {
                "method": "GET",
                "module": "services",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["data"]["resolved"])
        self.assertEqual(response.data["data"]["module"], "services")

    def test_gateway_integrations_applications_requires_auth_and_returns_company_scope(self):
        anonymous_response = self.client.get("/api/v1/gateway/integrations/applications/", format="json")
        self.assertEqual(anonymous_response.status_code, status.HTTP_401_UNAUTHORIZED)

        user_model = get_user_model()
        company = Company.objects.create(name="Registry Corp", code="registry-corp")
        department = Department.objects.create(company=company, name="Platform", code="platform")
        user = user_model.objects.create_user(
            email="registry@example.com",
            password="StrongPass123",
            smartphone_number="+821088880012",
        )
        UserCompanyMembership.objects.create(user=user, company=company, role="member", is_default=True)
        UserDepartmentMembership.objects.create(user=user, department=department, role="member")
        RegisteredApplication.objects.create(
            company=company,
            app_code="ops-console",
            app_name="Ops Console",
            app_domain="ops.example.com",
            app_base_url="https://ops.example.com",
            requires_sso=True,
        )

        self.client.force_authenticate(user=user)
        response = self.client.get("/api/v1/gateway/integrations/applications/", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["applications"]), 1)
        self.assertEqual(response.data["data"]["applications"][0]["app_code"], "ops-console")
