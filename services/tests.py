from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model

from accounts.models import Company, UserCompanyMembership
from services.models import RegisteredApplication, RegisteredFeature, RegisteredScreen, ServiceRegistry


class ServicesAPITestCase(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.company_a = Company.objects.create(name="Alpha Corp", code="alpha")
        self.company_b = Company.objects.create(name="Beta Corp", code="beta")
        self.user = user_model.objects.create_user(
            email="services@example.com",
            password="StrongPass123",
            smartphone_number="+821077770001",
        )
        UserCompanyMembership.objects.create(user=self.user, company=self.company_a, role="member", is_default=True)
        self.client.force_authenticate(user=self.user)

    def test_service_registry_lists_only_user_company_services(self):
        ServiceRegistry.objects.create(
            company=self.company_a,
            name="Billing Service",
            code="billing",
            description="Billing backend",
            base_path="/services/billing/",
            upstream_url="https://billing.internal/api/",
        )
        ServiceRegistry.objects.create(
            company=self.company_b,
            name="Inactive Service",
            code="crm",
            description="Other tenant backend",
            base_path="/services/crm/",
            upstream_url="https://crm.internal/api/",
        )

        response = self.client.get("/api/v1/services/", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["count"], 1)
        self.assertEqual(response.data["data"]["results"][0]["code"], "billing")

    def test_anonymous_user_cannot_list_services(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/services/", format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_and_list_registered_application(self):
        create_response = self.client.post(
            "/api/v1/services/applications/",
            {
                "company_id": str(self.company_a.id),
                "app_code": "alpha-hub",
                "app_name": "Alpha Hub",
                "app_description": "Main connected service",
                "app_domain": "alpha.example.com",
                "app_base_url": "https://alpha.example.com",
                "requires_sso": True,
            },
            format="json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(create_response.data["success"])
        self.assertEqual(create_response.data["data"]["app_code"], "alpha-hub")

        list_response = self.client.get("/api/v1/services/applications/", format="json")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data["data"]["count"], 1)
        self.assertEqual(list_response.data["data"]["results"][0]["app_name"], "Alpha Hub")

    def test_create_screen_and_feature_under_registered_application(self):
        application = RegisteredApplication.objects.create(
            company=self.company_a,
            app_code="ops-console",
            app_name="Ops Console",
            app_domain="ops.example.com",
            app_base_url="https://ops.example.com",
            requires_sso=True,
        )

        screen_response = self.client.post(
            "/api/v1/services/screens/",
            {
                "application_id": str(application.id),
                "screen_code": "dashboard",
                "screen_name": "Dashboard",
                "route_path": "/dashboard/",
            },
            format="json",
        )
        self.assertEqual(screen_response.status_code, status.HTTP_201_CREATED)

        screen_id = screen_response.data["data"]["id"]
        feature_response = self.client.post(
            "/api/v1/services/features/",
            {
                "application_id": str(application.id),
                "screen_id": screen_id,
                "feature_code": "dashboard-view",
                "feature_name": "Dashboard View",
                "feature_type": "view",
                "description": "Primary dashboard capability",
            },
            format="json",
        )
        self.assertEqual(feature_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(feature_response.data["data"]["feature_code"], "dashboard-view")

    def test_duplicate_application_code_fails_validation(self):
        RegisteredApplication.objects.create(
            company=self.company_a,
            app_code="duplicate-app",
            app_name="Duplicate App",
            app_domain="dup.example.com",
            app_base_url="https://dup.example.com",
            requires_sso=True,
        )

        response = self.client.post(
            "/api/v1/services/applications/",
            {
                "company_id": str(self.company_a.id),
                "app_code": "duplicate-app",
                "app_name": "Duplicate Again",
                "app_domain": "dup2.example.com",
                "app_base_url": "https://dup2.example.com",
                "requires_sso": True,
            },
            format="json",
        )

        payload = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(payload["success"])

    def test_inactive_application_cannot_receive_active_screen(self):
        application = RegisteredApplication.objects.create(
            company=self.company_a,
            app_code="legacy-app",
            app_name="Legacy App",
            app_domain="legacy.example.com",
            app_base_url="https://legacy.example.com",
            requires_sso=False,
            is_active=False,
        )

        response = self.client.post(
            "/api/v1/services/screens/",
            {
                "application_id": str(application.id),
                "screen_code": "legacy-screen",
                "screen_name": "Legacy Screen",
                "route_path": "/legacy/",
                "is_active": True,
            },
            format="json",
        )

        payload = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(payload["success"])

    def test_gateway_integrations_applications_returns_registered_apps(self):
        RegisteredApplication.objects.create(
            company=self.company_a,
            app_code="gamma-app",
            app_name="Gamma App",
            app_description="Gateway managed application",
            app_domain="gamma.example.com",
            app_base_url="https://gamma.example.com",
            requires_sso=True,
        )

        response = self.client.get("/api/v1/gateway/integrations/applications/", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["applications"]), 1)
        self.assertEqual(response.data["data"]["applications"][0]["app_code"], "gamma-app")
