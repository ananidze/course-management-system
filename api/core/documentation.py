"""
Reusable OpenAPI documentation components for consistent API documentation.
"""

from drf_spectacular.utils import OpenApiResponse, OpenApiExample, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


# Common Response Examples
class CommonResponses:
    """Common response examples used across the API."""

    SUCCESS_RESPONSE = OpenApiResponse(
        description="Operation completed successfully",
        examples=[
            OpenApiExample(
                "Success Response",
                value={
                    "success": True,
                    "message": "Operation completed successfully",
                    "data": None,
                },
            )
        ],
    )

    VALIDATION_ERROR = OpenApiResponse(
        description="Validation error",
        examples=[
            OpenApiExample(
                "Validation Error",
                value={
                    "success": False,
                    "message": "Validation failed",
                    "errors": {
                        "field_name": ["This field is required."],
                    },
                },
            )
        ],
    )

    NOT_FOUND = OpenApiResponse(
        description="Resource not found",
        examples=[
            OpenApiExample(
                "Not Found",
                value={
                    "success": False,
                    "message": "Resource not found",
                    "error_code": "NOT_FOUND",
                },
            )
        ],
    )

    PERMISSION_DENIED = OpenApiResponse(
        description="Permission denied",
        examples=[
            OpenApiExample(
                "Permission Denied",
                value={
                    "success": False,
                    "message": "You do not have permission to perform this action",
                    "error_code": "PERMISSION_DENIED",
                },
            )
        ],
    )

    UNAUTHORIZED = OpenApiResponse(
        description="Authentication required",
        examples=[
            OpenApiExample(
                "Unauthorized",
                value={
                    "success": False,
                    "message": "Authentication credentials were not provided",
                    "error_code": "UNAUTHORIZED",
                },
            )
        ],
    )


# Common Parameters
class CommonParameters:
    """Common parameters used across the API."""

    PAGE = OpenApiParameter(
        name="page",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        description="Page number for pagination",
        default=1,
    )

    PAGE_SIZE = OpenApiParameter(
        name="page_size",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        description="Number of items per page",
        default=10,
    )

    SEARCH = OpenApiParameter(
        name="search",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description="Search term for filtering results",
    )

    ORDERING = OpenApiParameter(
        name="ordering",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description="Order results by field (prefix with - for descending)",
    )


# Decorator Functions
def standard_responses(*status_codes):
    """Decorator to add standard responses to API endpoints."""
    responses = {}

    for status_code in status_codes:
        if status_code == 200:
            responses[200] = CommonResponses.SUCCESS_RESPONSE
        elif status_code == 201:
            responses[201] = CommonResponses.SUCCESS_RESPONSE
        elif status_code == 400:
            responses[400] = CommonResponses.VALIDATION_ERROR
        elif status_code == 401:
            responses[401] = CommonResponses.UNAUTHORIZED
        elif status_code == 403:
            responses[403] = CommonResponses.PERMISSION_DENIED
        elif status_code == 404:
            responses[404] = CommonResponses.NOT_FOUND

    return responses


def paginated_response(serializer_class, description="List retrieved successfully"):
    """Create a paginated response for list endpoints."""
    return OpenApiResponse(
        description=description,
        examples=[
            OpenApiExample(
                "Paginated Response",
                value={
                    "success": True,
                    "message": description,
                    "data": {
                        "count": 10,
                        "next": "http://localhost:8000/api/v1/endpoint/?page=2",
                        "previous": None,
                        "results": [
                            # This will be populated by the serializer
                        ],
                    },
                },
            )
        ],
    )
