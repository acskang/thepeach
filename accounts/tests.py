import json

from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from django.test import override_settings

from accounts.models import Company, Department, UserDepartmentMembership
from logs.models import AuthEventLog


class AccountsAPITestCase(APITestCase):
    def test_signup_login_and_profile_flow(self):
        company = Company.objects.create(name="Peach HQ", code="peach-hq")
        department = Department.objects.create(company=company, name="Platform", code="platform")
        signup_response = self.client.post(
            "/api/v1/auth/signup/",
            {
                "email": "tester@example.com",
                "full_name": "Tester Example",
                "smartphone_number": "+821012341234",
                "password": "StrongPass123",
            },
            format="json",
        )
        self.assertEqual(signup_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(signup_response.data["success"])
        self.assertEqual(signup_response.data["data"]["email"], "tester@example.com")

        user = get_user_model().objects.get(email="tester@example.com")
        user.company_memberships.create(company=company, role="member", is_default=True)
        UserDepartmentMembership.objects.create(user=user, department=department, role="member")

        login_response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": "tester@example.com",
                "password": "StrongPass123",
            },
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_response.data["data"])
        self.assertIn("refresh", login_response.data["data"])

        access_token = login_response.data["data"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        profile_response = self.client.get("/api/v1/auth/me/", format="json")

        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data["data"]["email"], "tester@example.com")
        self.assertEqual(profile_response.data["data"]["full_name"], "Tester Example")
        self.assertEqual(profile_response.data["data"]["smartphone_number"], "+821012341234")
        self.assertEqual(len(profile_response.data["data"]["companies"]), 1)
        self.assertEqual(len(profile_response.data["data"]["departments"]), 1)
        self.assertEqual(login_response.data["data"]["user"]["email"], "tester@example.com")

    def test_logout_blacklists_refresh_token(self):
        self.client.post(
            "/api/v1/auth/signup/",
            {
                "email": "logout@example.com",
                "full_name": "Logout User",
                "smartphone_number": "+821055551111",
                "password": "StrongPass123",
            },
            format="json",
        )
        login_response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": "logout@example.com",
                "password": "StrongPass123",
            },
            format="json",
        )

        access_token = login_response.data["data"]["access"]
        refresh_token = login_response.data["data"]["refresh"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        logout_response = self.client.post(
            "/api/v1/auth/logout/",
            {"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        self.assertTrue(logout_response.data["data"]["logged_out"])
        self.assertEqual(AuthEventLog.objects.filter(event_type=AuthEventLog.EVENT_LOGOUT).count(), 1)

    def test_smartphone_number_must_be_unique(self):
        self.client.post(
            "/api/v1/auth/signup/",
            {
                "email": "first@example.com",
                "full_name": "First User",
                "smartphone_number": "+821099990000",
                "password": "StrongPass123",
            },
            format="json",
        )

        response = self.client.post(
            "/api/v1/auth/signup/",
            {
                "email": "second@example.com",
                "full_name": "Second User",
                "smartphone_number": "+821099990000",
                "password": "StrongPass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_auth_root_exposes_sso_ready_metadata(self):
        response = self.client.get("/api/v1/auth/", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertTrue(response.data["data"]["architecture"]["sso_ready"])
        self.assertEqual(response.data["data"]["zone"], "public")

    def test_token_refresh_endpoint_works_under_auth_prefix(self):
        self.client.post(
            "/api/v1/auth/signup/",
            {
                "email": "refresh@example.com",
                "full_name": "Refresh User",
                "smartphone_number": "+821077770009",
                "password": "StrongPass123",
            },
            format="json",
        )
        login_response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": "refresh@example.com",
                "password": "StrongPass123",
            },
            format="json",
        )

        refresh_response = self.client.post(
            "/api/v1/auth/token/refresh/",
            {"refresh": login_response.data["data"]["refresh"]},
            format="json",
        )

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data["data"])

    def test_failed_login_attempt_is_logged(self):
        self.client.post(
            "/api/v1/auth/signup/",
            {
                "email": "failure@example.com",
                "full_name": "Failure User",
                "smartphone_number": "+821077770010",
                "password": "StrongPass123",
            },
            format="json",
        )

        response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": "failure@example.com",
                "password": "WrongPass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(AuthEventLog.objects.filter(event_type=AuthEventLog.EVENT_FAILURE).count(), 1)

    def test_signup_validation_failure_returns_standard_error_shape(self):
        response = self.client.post(
            "/api/v1/auth/signup/",
            {
                "email": "",
                "full_name": "",
                "password": "short",
            },
            format="json",
        )

        payload = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(payload["success"])
        self.assertIsNone(payload["data"])
        self.assertIn("code", payload["error"])

    @override_settings(
        ALLOWED_HOSTS=["testserver", "ops.thesysm.com", "thepeach.thesysm.com"],
        THEPEACH_INTERNAL_ALLOWED_HOSTS=("ops.thesysm.com",),
        THEPEACH_INTERNAL_REQUIRED_HEADERS=(),
    )
    def test_internal_auth_manifest_is_blocked_on_public_host(self):
        self.client.post(
            "/api/v1/auth/signup/",
            {
                "email": "internal-public-block@example.com",
                "full_name": "Internal Block",
                "smartphone_number": "+821077770011",
                "password": "StrongPass123",
            },
            format="json",
        )
        login_response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": "internal-public-block@example.com",
                "password": "StrongPass123",
            },
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['data']['access']}")

        response = self.client.get("/api/v1/auth/internal/", format="json", HTTP_HOST="thepeach.thesysm.com")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"]["code"], "internal_access_required")

    @override_settings(
        ALLOWED_HOSTS=["testserver", "ops.thesysm.com"],
        THEPEACH_INTERNAL_ALLOWED_HOSTS=("ops.thesysm.com",),
        THEPEACH_INTERNAL_REQUIRED_HEADERS=(),
    )
    def test_internal_auth_manifest_is_available_on_ops_host(self):
        self.client.post(
            "/api/v1/auth/signup/",
            {
                "email": "internal-ok@example.com",
                "full_name": "Internal Ok",
                "smartphone_number": "+821077770012",
                "password": "StrongPass123",
            },
            format="json",
        )
        login_response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": "internal-ok@example.com",
                "password": "StrongPass123",
            },
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['data']['access']}")

        response = self.client.get("/api/v1/auth/internal/", format="json", HTTP_HOST="ops.thesysm.com")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["zone"], "internal")
        self.assertIn("auth_event_summary", response.data["data"]["internal_endpoints"])

    @override_settings(
        ALLOWED_HOSTS=["testserver", "ops.thesysm.com"],
        THEPEACH_INTERNAL_ALLOWED_HOSTS=("ops.thesysm.com",),
        THEPEACH_INTERNAL_REQUIRED_HEADERS=("CF-Access-Authenticated-User-Email",),
    )
    def test_internal_auth_endpoint_can_require_proxy_header(self):
        self.client.post(
            "/api/v1/auth/signup/",
            {
                "email": "internal-header@example.com",
                "full_name": "Internal Header",
                "smartphone_number": "+821077770013",
                "password": "StrongPass123",
            },
            format="json",
        )
        login_response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": "internal-header@example.com",
                "password": "StrongPass123",
            },
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['data']['access']}")

        denied = self.client.get("/api/v1/auth/internal/", format="json", HTTP_HOST="ops.thesysm.com")
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)

        allowed = self.client.get(
            "/api/v1/auth/internal/",
            format="json",
            HTTP_HOST="ops.thesysm.com",
            HTTP_CF_ACCESS_AUTHENTICATED_USER_EMAIL="ops@example.com",
        )
        self.assertEqual(allowed.status_code, status.HTTP_200_OK)
