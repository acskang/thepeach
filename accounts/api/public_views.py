import logging

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from common.responses import success_response

from accounts.models import User
from accounts.serializers import (
    LogoutSerializer,
    PlatformTokenObtainPairSerializer,
    SignupSerializer,
    UserSerializer,
)
from accounts.services import (
    build_public_auth_manifest,
    handle_signup,
    issue_login_tokens,
    log_signup_attempt,
    logout_user,
    refresh_tokens,
)

auth_logger = logging.getLogger("accounts.auth")


class PublicAuthManifestView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return success_response(data=build_public_auth_manifest())


class SignupAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        handle_signup(serializer=serializer, request=self.request, auth_logger=auth_logger)

    def create(self, request, *args, **kwargs):
        log_signup_attempt(request=request, auth_logger=auth_logger)
        response = super().create(request, *args, **kwargs)
        return success_response(data=response.data, status_code=status.HTTP_201_CREATED)


class PlatformTokenObtainPairView(TokenObtainPairView):
    serializer_class = PlatformTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        response = issue_login_tokens(serializer=serializer, request=request, auth_logger=auth_logger)
        return success_response(data=response.data, status_code=response.status_code)


class PlatformTokenRefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        return success_response(data=refresh_tokens(request=request))


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = LogoutSerializer(data=request.data)
        logout_user(serializer=serializer, request=request, auth_logger=auth_logger)
        return success_response(data={"logged_out": True})


class ProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return success_response(data=UserSerializer(request.user).data)
