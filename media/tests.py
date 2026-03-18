import io
import json
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Company, Department, UserCompanyMembership, UserDepartmentMembership
from services.models import RegisteredApplication

from .models import PlatformLogoAsset

User = get_user_model()
TEST_MEDIA_ROOT = tempfile.mkdtemp(prefix="thepeach-media-tests-")


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class PlatformLogoAssetAPITestCase(APITestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.company = Company.objects.create(name="Logo Corp", code="logo-corp")
        self.other_company = Company.objects.create(name="Other Corp", code="other-corp")
        self.department = Department.objects.create(company=self.company, name="Design", code="design")
        self.user = User.objects.create_user(
            email="logo-admin@example.com",
            password="StrongPass123",
            full_name="Logo Admin",
            smartphone_number="+821077700001",
        )
        UserCompanyMembership.objects.create(user=self.user, company=self.company, role="member", is_default=True)
        UserDepartmentMembership.objects.create(user=self.user, department=self.department, role="manager")
        self.application = RegisteredApplication.objects.create(
            company=self.company,
            app_code="brand-portal",
            app_name="Brand Portal",
            app_domain="brand.example.com",
            app_base_url="https://brand.example.com",
            requires_sso=True,
        )
        self.other_application = RegisteredApplication.objects.create(
            company=self.other_company,
            app_code="other-portal",
            app_name="Other Portal",
            app_domain="other.example.com",
            app_base_url="https://other.example.com",
            requires_sso=True,
        )

    def _authenticate(self):
        self.client.force_authenticate(user=self.user)

    def _build_png_file(self, *, name="logo.png", size=(64, 64), color=(220, 120, 40)):
        stream = io.BytesIO()
        image = Image.new("RGB", size, color)
        image.save(stream, format="PNG")
        stream.seek(0)
        return SimpleUploadedFile(name, stream.getvalue(), content_type="image/png")

    def test_logo_upload_success(self):
        self._authenticate()
        response = self.client.post(
            "/api/v1/media/logos/",
            {
                "application_code": self.application.app_code,
                "logo_code": "brand-primary",
                "logo_name": "Brand Primary",
                "usage_type": "primary",
                "alt_text": "Brand primary logo",
                "image_file": self._build_png_file(),
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["logo_code"], "brand-primary")
        self.assertEqual(response.data["data"]["application"]["app_code"], self.application.app_code)

    def test_invalid_file_type_rejected(self):
        self._authenticate()
        response = self.client.post(
            "/api/v1/media/logos/",
            {
                "application_code": self.application.app_code,
                "logo_code": "bad-type",
                "logo_name": "Bad Type",
                "usage_type": "icon",
                "image_file": SimpleUploadedFile("bad.txt", b"not-an-image", content_type="text/plain"),
            },
        )

        payload = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(payload["success"])

    def test_oversized_file_rejected(self):
        self._authenticate()
        huge_file = SimpleUploadedFile(
            "huge.png",
            b"x" * (5 * 1024 * 1024 + 1),
            content_type="image/png",
        )
        response = self.client.post(
            "/api/v1/media/logos/",
            {
                "application_code": self.application.app_code,
                "logo_code": "huge-logo",
                "logo_name": "Huge Logo",
                "usage_type": "header",
                "image_file": huge_file,
            },
        )

        payload = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(payload["success"])

    def test_duplicate_logo_code_rejected(self):
        self._authenticate()
        PlatformLogoAsset.objects.create(
            application=self.application,
            logo_code="duplicate-code",
            logo_name="Existing Logo",
            original_file_name="existing.png",
            image_file=self._build_png_file(name="existing.png"),
            file_size=123,
            mime_type="image/png",
            width=64,
            height=64,
            created_by=self.user,
            updated_by=self.user,
        )

        response = self.client.post(
            "/api/v1/media/logos/",
            {
                "application_code": self.application.app_code,
                "logo_code": "duplicate-code",
                "logo_name": "Duplicate Logo",
                "usage_type": "header",
                "image_file": self._build_png_file(name="duplicate.png"),
            },
        )

        payload = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(payload["success"])

    def test_list_filtering_by_application(self):
        self._authenticate()
        PlatformLogoAsset.objects.create(
            application=self.application,
            logo_code="brand-list",
            logo_name="Brand List",
            original_file_name="brand.png",
            image_file=self._build_png_file(name="brand.png"),
            file_size=123,
            mime_type="image/png",
            width=64,
            height=64,
            created_by=self.user,
            updated_by=self.user,
        )
        PlatformLogoAsset.objects.create(
            application=self.other_application,
            logo_code="other-list",
            logo_name="Other List",
            original_file_name="other.png",
            image_file=self._build_png_file(name="other.png"),
            file_size=123,
            mime_type="image/png",
            width=64,
            height=64,
        )

        response = self.client.get(f"/api/v1/media/logos/?application={self.application.app_code}", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["count"], 1)
        self.assertEqual(response.data["data"]["results"][0]["logo_code"], "brand-list")

    def test_detail_retrieval(self):
        self._authenticate()
        logo = PlatformLogoAsset.objects.create(
            application=self.application,
            logo_code="detail-logo",
            logo_name="Detail Logo",
            original_file_name="detail.png",
            image_file=self._build_png_file(name="detail.png"),
            file_size=123,
            mime_type="image/png",
            width=64,
            height=64,
            created_by=self.user,
            updated_by=self.user,
        )

        response = self.client.get(f"/api/v1/media/logos/{logo.id}/", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["logo_code"], "detail-logo")

    def test_metadata_update_success(self):
        self._authenticate()
        logo = PlatformLogoAsset.objects.create(
            application=self.application,
            logo_code="meta-logo",
            logo_name="Meta Logo",
            original_file_name="meta.png",
            image_file=self._build_png_file(name="meta.png"),
            file_size=123,
            mime_type="image/png",
            width=64,
            height=64,
            created_by=self.user,
            updated_by=self.user,
        )

        response = self.client.patch(
            f"/api/v1/media/logos/{logo.id}/",
            {
                "logo_name": "Updated Meta Logo",
                "usage_type": "header",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["logo_name"], "Updated Meta Logo")
        self.assertEqual(response.data["data"]["usage_type"], "header")

    def test_deactivate_success(self):
        self._authenticate()
        logo = PlatformLogoAsset.objects.create(
            application=self.application,
            logo_code="deactivate-logo",
            logo_name="Deactivate Logo",
            original_file_name="deactivate.png",
            image_file=self._build_png_file(name="deactivate.png"),
            file_size=123,
            mime_type="image/png",
            width=64,
            height=64,
            is_active=True,
            created_by=self.user,
            updated_by=self.user,
        )

        response = self.client.post(f"/api/v1/media/logos/{logo.id}/deactivate/", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        logo.refresh_from_db()
        self.assertFalse(logo.is_active)

    def test_unauthorized_upload_rejected(self):
        response = self.client.post(
            "/api/v1/media/logos/",
            {
                "application_code": self.application.app_code,
                "logo_code": "anon-logo",
                "logo_name": "Anonymous Logo",
                "usage_type": "icon",
                "image_file": self._build_png_file(name="anon.png"),
            },
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
