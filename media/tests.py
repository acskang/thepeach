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

from .models import SharedMediaAsset

User = get_user_model()
TEST_MEDIA_ROOT = tempfile.mkdtemp(prefix="thepeach-shared-media-tests-")


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT, THEPEACH_MEDIA_MAX_UPLOAD_BYTES=1024 * 1024)
class SharedMediaAssetAPITestCase(APITestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(
            email="asset-admin@example.com",
            password="StrongPass123",
            full_name="Asset Admin",
            smartphone_number="+821077700123",
        )

    def _authenticate(self):
        self.client.force_authenticate(user=self.user)

    def _build_png_file(self, *, name="asset.png", size=(64, 64), color=(220, 120, 40)):
        stream = io.BytesIO()
        image = Image.new("RGB", size, color)
        image.save(stream, format="PNG")
        stream.seek(0)
        return SimpleUploadedFile(name, stream.getvalue(), content_type="image/png")

    def test_upload_success(self):
        self._authenticate()
        response = self.client.post(
            "/api/v1/media/assets/",
            {
                "title": "Shared Hero",
                "alt_text": "Shared hero image",
                "description": "Reusable hero image",
                "file": self._build_png_file(),
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["title"], "Shared Hero")
        self.assertEqual(response.data["data"]["mime_type"], "image/png")
        self.assertFalse(response.data["data"]["deduplicated"])

    def test_invalid_file_type_rejected(self):
        self._authenticate()
        response = self.client.post(
            "/api/v1/media/assets/",
            {
                "title": "Bad Type",
                "file": SimpleUploadedFile("bad.txt", b"not-an-image", content_type="text/plain"),
            },
        )

        payload = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(payload["success"])

    def test_corrupted_file_rejected(self):
        self._authenticate()
        response = self.client.post(
            "/api/v1/media/assets/",
            {
                "title": "Broken Image",
                "file": SimpleUploadedFile("broken.png", b"not-really-a-png", content_type="image/png"),
            },
        )

        payload = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(payload["success"])

    def test_oversized_file_rejected(self):
        self._authenticate()
        huge_file = SimpleUploadedFile(
            "huge.png",
            b"x" * (1024 * 1024 + 1),
            content_type="image/png",
        )
        response = self.client.post(
            "/api/v1/media/assets/",
            {
                "title": "Huge Asset",
                "file": huge_file,
            },
        )

        payload = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(payload["success"])

    def test_duplicate_checksum_returns_existing_asset(self):
        self._authenticate()
        first = self.client.post(
            "/api/v1/media/assets/",
            {
                "title": "Shared Asset One",
                "file": self._build_png_file(name="same.png"),
            },
        )
        second = self.client.post(
            "/api/v1/media/assets/",
            {
                "title": "Shared Asset Two",
                "file": self._build_png_file(name="same-copy.png"),
            },
        )

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(first.data["data"]["id"], second.data["data"]["id"])
        self.assertTrue(second.data["data"]["deduplicated"])

    def test_list_endpoint(self):
        self._authenticate()
        SharedMediaAsset.objects.create(
            file=self._build_png_file(name="list.png"),
            original_file_name="list.png",
            stored_file_name="list.png",
            file_size=123,
            mime_type="image/png",
            width=64,
            height=64,
            checksum_sha256="a" * 64,
            title="List Asset",
            created_by=self.user,
        )

        response = self.client.get("/api/v1/media/assets/", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["count"], 1)

    def test_detail_endpoint(self):
        self._authenticate()
        asset = SharedMediaAsset.objects.create(
            file=self._build_png_file(name="detail.png"),
            original_file_name="detail.png",
            stored_file_name="detail.png",
            file_size=123,
            mime_type="image/png",
            width=64,
            height=64,
            checksum_sha256="b" * 64,
            title="Detail Asset",
            created_by=self.user,
        )

        response = self.client.get(f"/api/v1/media/assets/{asset.id}/", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["title"], "Detail Asset")

    def test_metadata_update_success(self):
        self._authenticate()
        asset = SharedMediaAsset.objects.create(
            file=self._build_png_file(name="meta.png"),
            original_file_name="meta.png",
            stored_file_name="meta.png",
            file_size=123,
            mime_type="image/png",
            width=64,
            height=64,
            checksum_sha256="c" * 64,
            title="Meta Asset",
            created_by=self.user,
        )

        response = self.client.patch(
            f"/api/v1/media/assets/{asset.id}/",
            {
                "title": "Updated Shared Asset",
                "description": "New description",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["title"], "Updated Shared Asset")
        self.assertEqual(response.data["data"]["description"], "New description")

    def test_deactivate_success(self):
        self._authenticate()
        asset = SharedMediaAsset.objects.create(
            file=self._build_png_file(name="deactivate.png"),
            original_file_name="deactivate.png",
            stored_file_name="deactivate.png",
            file_size=123,
            mime_type="image/png",
            width=64,
            height=64,
            checksum_sha256="d" * 64,
            title="Deactivate Asset",
            is_active=True,
            created_by=self.user,
        )

        response = self.client.post(f"/api/v1/media/assets/{asset.id}/deactivate/", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        asset.refresh_from_db()
        self.assertFalse(asset.is_active)

    def test_unauthorized_write_rejected(self):
        response = self.client.post(
            "/api/v1/media/assets/",
            {
                "title": "Anonymous Asset",
                "file": self._build_png_file(name="anon.png"),
            },
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_response_shape_is_stable(self):
        self._authenticate()
        response = self.client.post(
            "/api/v1/media/assets/",
            {
                "title": "Stable Shape",
                "file": self._build_png_file(name="shape.png"),
            },
        )

        self.assertIn("success", response.data)
        self.assertIn("data", response.data)
        self.assertIn("error", response.data)
