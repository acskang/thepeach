from rest_framework import status
from rest_framework.exceptions import APIException


class ThePeachAuthUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "ThePeach auth service is unavailable."
    default_code = "thepeach_auth_unavailable"


class ThePeachAuthContractError(APIException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = "ThePeach auth service returned an unexpected payload."
    default_code = "thepeach_auth_contract_error"


def api_exception_handler(exc, context):
    from rest_framework.views import exception_handler

    response = exception_handler(exc, context)
    if response is None:
        return response

    message = "Request failed."
    details = response.data
    if isinstance(response.data, dict) and "detail" in response.data:
        message = response.data["detail"]

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
