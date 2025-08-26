from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from api.core.documentation import CommonResponses
from api.core.responses import APIResponse


@extend_schema(
    summary="Health Check",
    description="Check if the API is running and healthy",
    responses={
        200: CommonResponses.SUCCESS_RESPONSE,
    },
    tags=["health"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return APIResponse.success(
        data={
            "status": "healthy",
            "version": "v1",
            "timestamp": request.data.get("timestamp", None),
        },
        message="API is healthy",
    )
