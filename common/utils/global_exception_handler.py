from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    # Get the default response from DRF
    response = exception_handler(exc, context)

    # If response is None, it means the exception is unhandled
    if response is None:
        return Response(
            {
                "error": "Unfortunately, An unexpected error occurred.",
                "details": "Please contact support if this issue persists.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
