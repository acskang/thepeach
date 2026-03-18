from rest_framework import generics, permissions, status
from rest_framework.views import APIView

from common.responses import success_response

from .models import RegisteredApplication, RegisteredFeature, RegisteredScreen
from .registry_service import (
    create_registry_entry,
    deactivate_registry_entry,
    get_registered_application_queryset,
    get_registered_feature_queryset,
    get_registered_screen_queryset,
    get_service_registry_queryset,
    update_registry_entry,
)
from .serializers import (
    RegisteredApplicationSerializer,
    RegisteredFeatureSerializer,
    RegisteredScreenSerializer,
    ServiceRegistrySerializer,
)


class ServiceRegistryListAPIView(generics.ListAPIView):
    serializer_class = ServiceRegistrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_service_registry_queryset(user=self.request.user)


class RegisteredApplicationListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = RegisteredApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_registered_application_queryset(user=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return success_response(data=response.data, status_code=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        create_registry_entry(serializer=serializer, request=self.request, registry_type="application")


class RegisteredApplicationDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = RegisteredApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = RegisteredApplication.objects.select_related("company")

    def get_queryset(self):
        return get_registered_application_queryset(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return success_response(data=response.data, status_code=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return success_response(data=response.data, status_code=response.status_code)

    def perform_update(self, serializer):
        update_registry_entry(serializer=serializer, request=self.request, registry_type="application")


class RegisteredApplicationDeactivateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        instance = get_registered_application_queryset(user=request.user).get(pk=pk)
        deactivate_registry_entry(instance=instance, request=request, registry_type="application")
        return success_response(data={"deactivated": True, "id": str(instance.pk)})


class RegisteredScreenListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = RegisteredScreenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = get_registered_screen_queryset(user=self.request.user)
        application_id = self.request.query_params.get("application_id")
        if application_id:
            queryset = queryset.filter(application_id=application_id)
        return queryset

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return success_response(data=response.data, status_code=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        create_registry_entry(serializer=serializer, request=self.request, registry_type="screen")


class RegisteredScreenDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = RegisteredScreenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_registered_screen_queryset(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return success_response(data=response.data, status_code=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return success_response(data=response.data, status_code=response.status_code)

    def perform_update(self, serializer):
        update_registry_entry(serializer=serializer, request=self.request, registry_type="screen")


class RegisteredScreenDeactivateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        instance = get_registered_screen_queryset(user=request.user).get(pk=pk)
        deactivate_registry_entry(instance=instance, request=request, registry_type="screen")
        return success_response(data={"deactivated": True, "id": str(instance.pk)})


class RegisteredFeatureListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = RegisteredFeatureSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = get_registered_feature_queryset(user=self.request.user)
        application_id = self.request.query_params.get("application_id")
        if application_id:
            queryset = queryset.filter(application_id=application_id)
        screen_id = self.request.query_params.get("screen_id")
        if screen_id:
            queryset = queryset.filter(screen_id=screen_id)
        return queryset

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return success_response(data=response.data, status_code=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        create_registry_entry(serializer=serializer, request=self.request, registry_type="feature")


class RegisteredFeatureDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = RegisteredFeatureSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_registered_feature_queryset(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return success_response(data=response.data, status_code=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return success_response(data=response.data, status_code=response.status_code)

    def perform_update(self, serializer):
        update_registry_entry(serializer=serializer, request=self.request, registry_type="feature")


class RegisteredFeatureDeactivateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        instance = get_registered_feature_queryset(user=request.user).get(pk=pk)
        deactivate_registry_entry(instance=instance, request=request, registry_type="feature")
        return success_response(data={"deactivated": True, "id": str(instance.pk)})
