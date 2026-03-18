from django.urls import path

from .web_views import AccountHomePageView, LoginPageView, LogoutPageView, SignupPageView

app_name = "accounts-web"

urlpatterns = [
    path("signup/", SignupPageView.as_view(), name="signup-page"),
    path("login/", LoginPageView.as_view(), name="login-page"),
    path("logout/", LogoutPageView.as_view(), name="logout-page"),
    path("home/", AccountHomePageView.as_view(), name="home-page"),
]
