from django.views.generic import TemplateView


class SignupPageView(TemplateView):
    template_name = "accounts/signup.html"


class LoginPageView(TemplateView):
    template_name = "accounts/login.html"


class AccountHomePageView(TemplateView):
    template_name = "accounts/home.html"


class LogoutPageView(TemplateView):
    template_name = "accounts/logout.html"
