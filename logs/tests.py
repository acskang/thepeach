from rest_framework import status
from rest_framework.test import APITestCase

from logs.models import APIRequestLog, AuthEventLog


class LogsPersistenceTestCase(APITestCase):
    def test_api_requests_are_persisted(self):
        response = self.client.get("/api/v1/health/", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(APIRequestLog.objects.count(), 1)

        entry = APIRequestLog.objects.get()
        self.assertEqual(entry.path, "/api/v1/health/")
        self.assertEqual(entry.status_code, status.HTTP_200_OK)

    def test_auth_events_are_persisted(self):
        self.client.post(
            "/api/v1/auth/signup/",
            {
                "email": "audit@example.com",
                "display_name": "Audit",
                "smartphone_number": "+821033330001",
                "password": "StrongPass123",
            },
            format="json",
        )
        self.client.post(
            "/api/v1/auth/login/",
            {
                "email": "audit@example.com",
                "password": "StrongPass123",
            },
            format="json",
        )

        self.assertEqual(AuthEventLog.objects.filter(event_type=AuthEventLog.EVENT_SIGNUP).count(), 1)
        self.assertEqual(AuthEventLog.objects.filter(event_type=AuthEventLog.EVENT_LOGIN).count(), 1)
