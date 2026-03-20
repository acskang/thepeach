import io
from urllib import error
from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.auth.client import ThePeachAuthClient
from core.exceptions import ThePeachAuthUnavailable


AUTH_PAYLOAD = {
    "success": True,
    "data": {
        "id": "user-123",
        "email": "remote@example.com",
        "full_name": "Remote User",
        "display_name": "Remote User",
        "first_name": "Remote",
        "last_name": "User",
        "smartphone_number": "+821012341234",
        "external_id": "erp-99",
        "companies": [
            {
                "id": "company-1",
                "name": "Peach HQ",
                "code": "peach-hq",
                "is_active": True,
            }
        ],
        "departments": [
            {
                "id": "department-1",
                "name": "Platform",
                "code": "platform",
                "is_active": True,
                "company": {
                    "id": "company-1",
                    "name": "Peach HQ",
                    "code": "peach-hq",
                    "is_active": True,
                },
            }
        ],
        "is_active": True,
    },
    "error": None,
}


class TrustedPortalAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch.object(ThePeachAuthClient, "_fetch_profile", return_value=(AUTH_PAYLOAD, 200, {}))
    def test_example_endpoint_uses_thepeach_auth_me(self, mocked_fetch):
        response = self.client.get(
            "/api/v1/example/auth-status/",
            HTTP_AUTHORIZATION="Bearer access-token",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["user"]["email"], "remote@example.com")
        self.assertEqual(response.data["data"]["user"]["company_ids"], ["company-1"])
        mocked_fetch.assert_called_once()

    def test_example_endpoint_requires_token(self):
        response = self.client.get("/api/v1/example/auth-status/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])

    @patch.object(ThePeachAuthClient, "authenticate", side_effect=ThePeachAuthUnavailable("ThePeach auth service timed out."))
    def test_example_endpoint_handles_upstream_timeout(self, mocked_authenticate):
        response = self.client.get(
            "/api/v1/example/auth-status/",
            HTTP_AUTHORIZATION="Bearer access-token",
        )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data["error"]["code"], "thepeach_auth_unavailable")
        mocked_authenticate.assert_called_once()

    @patch.object(ThePeachAuthClient, "_fetch_profile", return_value=(AUTH_PAYLOAD, 200, {}))
    def test_home_view_uses_middleware_populated_remote_user(self, mocked_fetch):
        response = self.client.get("/", HTTP_AUTHORIZATION="Bearer access-token")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Trusted Portal")
        self.assertContains(response, "Auth Status API")
        self.assertContains(response, "remote@example.com")
        mocked_fetch.assert_called_once()

    @patch.object(ThePeachAuthClient, "_fetch_profile", return_value=(AUTH_PAYLOAD, 200, {}))
    def test_auth_me_html_view_renders(self, mocked_fetch):
        response = self.client.get("/api/v1/auth/me/", HTTP_AUTHORIZATION="Bearer access-token")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Authenticated user context from ThePeach upstream auth")
        self.assertContains(response, "remote@example.com")
        mocked_fetch.assert_called_once()

    @patch.object(ThePeachAuthClient, "_fetch_profile", return_value=(AUTH_PAYLOAD, 200, {}))
    def test_auth_me_json_view_returns_payload(self, mocked_fetch):
        response = self.client.get(
            "/api/v1/auth/me/",
            HTTP_AUTHORIZATION="Bearer access-token",
            HTTP_ACCEPT="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["user"]["email"], "remote@example.com")
        mocked_fetch.assert_called_once()

    def test_auth_me_html_view_renders_without_token(self):
        response = self.client.get("/api/v1/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "How to use this route")
        self.assertContains(response, "No token supplied")

    def test_auth_me_json_requires_token(self):
        response = self.client.get("/api/v1/auth/me/", HTTP_ACCEPT="application/json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "not_authenticated")

    def test_login_page_renders(self):
        response = self.client.get("/auth/login/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Sign in with your existing ThePeach account")
        self.assertContains(response, "Open ThePeach Login")

    @patch.object(ThePeachAuthClient, "login", return_value={"access": "access-token", "user": AUTH_PAYLOAD["data"]})
    def test_session_login_uses_thepeach_upstream(self, mocked_login):
        response = self.client.post(
            "/auth/session/login/",
            {"email": "remote@example.com", "password": "StrongPass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(self.client.session["thepeach_access_token"], "access-token")
        mocked_login.assert_called_once()

    def test_session_login_requires_credentials(self):
        response = self.client.post("/auth/session/login/", {"email": ""}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"]["code"], "invalid_credentials")

    @patch("core.auth.client.request.urlopen")
    def test_client_login_raises_contract_error_for_bad_credentials(self, mocked_urlopen):
        payload = b'{"success": false, "data": null, "error": {"code": "authentication_failed", "message": "Invalid email or password."}}'
        mocked_urlopen.side_effect = error.HTTPError(
            url="http://localhost:8000/api/v1/auth/login/",
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=io.BytesIO(payload),
        )

        client = ThePeachAuthClient()
        with self.assertRaisesMessage(Exception, "Invalid email or password."):
            client.login(email="remote@example.com", password="wrong")

    @patch("core.auth.client.request.urlopen")
    def test_client_login_falls_back_to_alternate_local_port_after_404(self, mocked_urlopen):
        success_body = io.BytesIO(
            b'{"success": true, "data": {"access": "access-token", "user": {"email": "remote@example.com"}}, "error": null}'
        )

        class FakeResponse:
            def __init__(self, body):
                self.body = body
                self.status = 200
                self.headers = {}

            def read(self):
                return self.body.read()

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        def side_effect(request_obj, timeout=None):
            if request_obj.full_url.startswith("http://localhost:8000/"):
                raise error.HTTPError(
                    url=request_obj.full_url,
                    code=404,
                    msg="Not Found",
                    hdrs=None,
                    fp=io.BytesIO(b""),
                )
            return FakeResponse(success_body)

        mocked_urlopen.side_effect = side_effect

        client = ThePeachAuthClient()
        payload = client.login(
            email="remote@example.com",
            password="StrongPass123",
            request_host="localhost:8000",
        )

        self.assertEqual(payload["access"], "access-token")

    @patch("core.auth.client.request.urlopen")
    def test_client_login_surfaces_cloudflare_1010_block(self, mocked_urlopen):
        mocked_urlopen.side_effect = error.HTTPError(
            url="https://thepeach.thesysm.com/api/v1/auth/login/",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b"error code: 1010"),
        )

        client = ThePeachAuthClient()
        with self.assertRaisesMessage(Exception, "Cloudflare 1010"):
            client.login(email="remote@example.com", password="StrongPass123")
