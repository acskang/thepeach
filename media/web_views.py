from django.views.generic import TemplateView


class LogoListPageView(TemplateView):
    template_name = "media/logos/list.html"


class LogoUploadPageView(TemplateView):
    template_name = "media/logos/upload.html"


class LogoFormPageView(TemplateView):
    template_name = "media/logos/form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["logo_id"] = self.kwargs.get("pk", "")
        return context
