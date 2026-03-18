from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


class PlatformAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A platform error occurred."
    default_code = "platform_error"


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    message = "Request failed."
    details = response.data

    if isinstance(response.data, dict):
        if "detail" in response.data:
            message = response.data["detail"]
        elif "non_field_errors" in response.data:
            message = response.data["non_field_errors"]

    response.data = {
        "success": False,
        "data": None,
        "error": {
            "code": getattr(exc, "default_code", "error"),
            "message": message,
            "details": details,
        },
    }
    return response
