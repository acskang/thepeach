from accounts.api.internal_views import InternalAuthEventSummaryAPIView, InternalAuthManifestView
from accounts.api.public_views import (
    LogoutAPIView,
    PlatformTokenObtainPairView,
    PlatformTokenRefreshView,
    ProfileAPIView,
    PublicAuthManifestView,
    SignupAPIView,
)

AuthArchitectureView = PublicAuthManifestView
