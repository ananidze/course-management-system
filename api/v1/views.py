from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse
from api.core.responses import APIResponse


@extend_schema(
    summary="Health Check",
    description="Check if the API is running and healthy",
    responses={
        200: OpenApiResponse(
            description="API is healthy",
            examples=[
                {
                    "success": True,
                    "message": "API is healthy",
                    "data": {"status": "healthy", "version": "v1"},
                }
            ],
        )
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
