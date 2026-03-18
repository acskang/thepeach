from rest_framework import serializers


class GatewayRouteResolveSerializer(serializers.Serializer):
    method = serializers.ChoiceField(
        choices=["GET", "POST", "PUT", "PATCH", "DELETE"],
        default="GET",
    )
    module = serializers.ChoiceField(
        choices=["auth", "health", "media", "services", "gateway"],
        required=False,
    )
    service_code = serializers.SlugField(required=False)
    path = serializers.CharField(required=False, allow_blank=False, max_length=255)

    def validate(self, attrs):
        module = attrs.get("module")
        service_code = attrs.get("service_code")
        path = attrs.get("path")

        if not module and not service_code and not path:
            raise serializers.ValidationError(
                "At least one of module, service_code, or path is required."
            )

        return attrs
