from django.views.generic import TemplateView


class AssetListPageView(TemplateView):
    template_name = "media/assets/list.html"


class AssetUploadPageView(TemplateView):
    template_name = "media/assets/upload.html"


class AssetFormPageView(TemplateView):
    template_name = "media/assets/form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["asset_id"] = self.kwargs.get("pk", "")
        return context
