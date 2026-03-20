from django.urls import path

from accounts.api.public_views import (
    LogoutAPIView,
    PlatformTokenObtainPairView,
    PlatformTokenRefreshView,
    ProfileAPIView,
    PublicAuthManifestView,
    SignupAPIView,
)

urlpatterns = [
    path("", PublicAuthManifestView.as_view(), name="auth_root"),
    path("signup/", SignupAPIView.as_view(), name="signup"),
    path("login/", PlatformTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", PlatformTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("me/", ProfileAPIView.as_view(), name="me"),
]
