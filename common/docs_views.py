from django.views.generic import TemplateView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from common.responses import success_response

from .docs_service import (
    build_document_detail_context,
    build_docs_hub_context,
    get_all_documents,
    get_document_by_slug,
)


class DocsHubView(TemplateView):
    template_name = "docs/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_docs_hub_context())
        return context


class DocsDetailView(TemplateView):
    template_name = "docs/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_document_detail_context(self.kwargs["slug"]))
        return context


class DocsIndexAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return success_response(
            data={
                "documents": get_all_documents(),
            }
        )


class DocsDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug, *args, **kwargs):
        return success_response(
            data=get_document_by_slug(slug),
        )
