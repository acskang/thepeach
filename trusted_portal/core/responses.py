from rest_framework import status
from rest_framework.response import Response


def success_response(data=None, status_code=status.HTTP_200_OK):
    return Response(
        {
            "success": True,
            "data": {} if data is None else data,
            "error": None,
        },
        status=status_code,
    )


def error_response(message, code="error", details=None, status_code=status.HTTP_400_BAD_REQUEST):
    return Response(
        {
            "success": False,
            "data": None,
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            },
        },
        status=status_code,
    )
