from django.urls import path

from .views import AuthMeAPIView, AuthStatusAPIView, SessionLoginAPIView, SessionLogoutAPIView, home, login_page

urlpatterns = [
    path("", home, name="home"),
    path("auth/login/", login_page, name="login"),
    path("auth/logout/", SessionLogoutAPIView.as_view(), name="logout"),
    path("auth/session/login/", SessionLoginAPIView.as_view(), name="session-login"),
    path("api/v1/auth/me/", AuthMeAPIView.as_view(), name="auth-me"),
    path("api/v1/example/auth-status/", AuthStatusAPIView.as_view(), name="auth-status"),
]
