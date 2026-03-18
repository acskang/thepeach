from django.views.generic import TemplateView


class ApplicationRegistryListPageView(TemplateView):
    template_name = "services/applications/list.html"


class ApplicationRegistryFormPageView(TemplateView):
    template_name = "services/applications/form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["application_id"] = self.kwargs.get("pk", "")
        return context
