import importlib
import os
import sys

from django.test import SimpleTestCase
from django.test import override_settings
from django.urls import reverse


class StartupSafetyTests(SimpleTestCase):
    def test_project_settings_package_does_not_alias_local_settings(self):
        sys.modules.pop("project.settings", None)
        module = importlib.import_module("project.settings")
        self.assertFalse(hasattr(module, "DEBUG"))

    def test_wsgi_requires_explicit_settings_module(self):
        original = os.environ.pop("DJANGO_SETTINGS_MODULE", None)
        sys.modules.pop("project.wsgi", None)

        try:
            with self.assertRaises(RuntimeError):
                importlib.import_module("project.wsgi")
        finally:
            if original is not None:
                os.environ["DJANGO_SETTINGS_MODULE"] = original
            sys.modules.pop("project.wsgi", None)

    def test_asgi_requires_explicit_settings_module(self):
        original = os.environ.pop("DJANGO_SETTINGS_MODULE", None)
        sys.modules.pop("project.asgi", None)

        try:
            with self.assertRaises(RuntimeError):
                importlib.import_module("project.asgi")
        finally:
            if original is not None:
                os.environ["DJANGO_SETTINGS_MODULE"] = original
            sys.modules.pop("project.asgi", None)


class PlatformUITests(SimpleTestCase):
    databases = {"default"}

    def test_homepage_resolves(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ThePeach Platform")
        self.assertContains(response, "Applications")
        self.assertContains(response, "Assets")

    @override_settings(
        ALLOWED_HOSTS=["testserver", "ops.thesysm.com", "thepeach.thesysm.com"],
        THEPEACH_INTERNAL_ALLOWED_HOSTS=("ops.thesysm.com",),
        THEPEACH_INTERNAL_REQUIRED_HEADERS=(),
    )
    def test_admin_is_blocked_on_public_host(self):
        response = self.client.get("/admin/", HTTP_HOST="thepeach.thesysm.com")

        self.assertEqual(response.status_code, 403)

    @override_settings(
        ALLOWED_HOSTS=["testserver", "ops.thesysm.com"],
        THEPEACH_INTERNAL_ALLOWED_HOSTS=("ops.thesysm.com",),
        THEPEACH_INTERNAL_REQUIRED_HEADERS=(),
    )
    def test_admin_is_accessible_on_ops_host(self):
        response = self.client.get("/admin/", HTTP_HOST="ops.thesysm.com")

        self.assertNotEqual(response.status_code, 403)


class DocumentationPortalTests(SimpleTestCase):
    databases = {"default"}

    def test_docs_index_returns_200(self):
        response = self.client.get(reverse("docs-index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Platform Documentation")
        self.assertContains(response, "Featured Core Documents")

    def test_docs_index_contains_expected_featured_docs(self):
        response = self.client.get(reverse("docs-index"))

        self.assertContains(response, "Platform Overview")
        self.assertContains(response, "Production Deployment")
        self.assertContains(response, "Shared Media Server")

    def test_docs_index_contains_category_grouping(self):
        response = self.client.get(reverse("docs-index"))

        self.assertContains(response, "Platform Foundations")
        self.assertContains(response, "Operations And Deployment")

    def test_docs_detail_returns_200_for_valid_slug(self):
        response = self.client.get(reverse("docs-detail", kwargs={"slug": "shared-media-server"}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Shared Media Server")
        self.assertContains(response, "Centralized shared image storage")

    def test_docs_detail_renders_markdown_heading_and_code(self):
        response = self.client.get(
            reverse("docs-detail", kwargs={"slug": "central-auth-and-application-registry"})
        )

        self.assertContains(response, "<h1", html=False)
        self.assertContains(response, "<code>", html=False)

    def test_unknown_slug_returns_404(self):
        response = self.client.get("/docs/not-a-real-document/")

        self.assertEqual(response.status_code, 404)

    def test_path_traversal_style_slug_is_rejected(self):
        response = self.client.get("/docs/..%2Fmanage.py/")

        self.assertEqual(response.status_code, 404)

    def test_docs_api_index_has_standard_response_shape(self):
        response = self.client.get("/api/v1/docs/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.data)
        self.assertIn("data", response.data)
        self.assertIn("error", response.data)
        self.assertTrue(response.data["success"])
        self.assertIn("documents", response.data["data"])

    def test_docs_api_detail_has_standard_response_shape(self):
        response = self.client.get("/api/v1/docs/shared-media-server/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["slug"], "shared-media-server")
        self.assertEqual(response.data["data"]["file_path"], "docs/shared-media-server.md")
