import importlib
import os
import sys

from django.test import SimpleTestCase
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
    def test_homepage_resolves(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ThePeach Platform")
        self.assertContains(response, "Applications")
        self.assertContains(response, "Logos")
