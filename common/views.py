from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from common.responses import success_response
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "home.html"


class PlatformHealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return success_response(
            data={
                "status": "ok",
                "service": "thepeach-platform",
                "version": "v1",
            }
        )
