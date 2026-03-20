from urllib.parse import urlencode

from django.urls import reverse
from django.views.generic import RedirectView, TemplateView


class AuthModalRedirectView(RedirectView):
    permanent = False
    auth_tab = "login"

    def get_redirect_url(self, *args, **kwargs):
        query = {"auth": self.auth_tab}
        next_url = self.request.GET.get("next")
        if next_url:
            query["next"] = next_url
        return f"{reverse('home')}?{urlencode(query)}"


class SignupPageView(AuthModalRedirectView):
    auth_tab = "signup"


class LoginPageView(AuthModalRedirectView):
    auth_tab = "login"


class AccountHomePageView(TemplateView):
    template_name = "accounts/home.html"


class LogoutPageView(AuthModalRedirectView):
    auth_tab = "logout"
