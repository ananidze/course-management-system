from rest_framework.response import Response
from rest_framework import status
from typing import Any, Dict, Optional


class APIResponse:
    @staticmethod
    def success(
        data: Any = None,
        message: Optional[str] = None,
        status_code: int = status.HTTP_200_OK,
        **kwargs,
    ) -> Response:
        response_data = {"success": True, "data": data, **kwargs}

        if message is not None:
            response_data["message"] = message

        response_data = {k: v for k, v in response_data.items() if v is not None}

        return Response(response_data, status=status_code)

    @staticmethod
    def error(
        message: str = "An error occurred",
        errors: Optional[Dict] = None,
        error_code: Optional[str] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        **kwargs,
    ) -> Response:
        response_data = {
            "success": False,
            "message": message,
            "errors": errors,
            "error_code": error_code,
            **kwargs,
        }

        response_data = {k: v for k, v in response_data.items() if v is not None}

        return Response(response_data, status=status_code)

    @staticmethod
    def created(data: Any = None, message: Optional[str] = None, **kwargs) -> Response:
        return APIResponse.success(data, message, status.HTTP_201_CREATED, **kwargs)

    @staticmethod
    def updated(data: Any = None, message: Optional[str] = None, **kwargs) -> Response:
        return APIResponse.success(data, message, status.HTTP_200_OK, **kwargs)

    @staticmethod
    def deleted(message: Optional[str] = None, **kwargs) -> Response:
        return APIResponse.success(None, message, status.HTTP_204_NO_CONTENT, **kwargs)

    @staticmethod
    def not_found(
        message: str = "Resource not found",
        error_code: str = "RESOURCE_NOT_FOUND",
        **kwargs,
    ) -> Response:
        return APIResponse.error(
            message,
            error_code=error_code,
            status_code=status.HTTP_404_NOT_FOUND,
            **kwargs,
        )

    @staticmethod
    def forbidden(
        message: str = "Access denied", error_code: str = "ACCESS_DENIED", **kwargs
    ) -> Response:
        return APIResponse.error(
            message,
            error_code=error_code,
            status_code=status.HTTP_403_FORBIDDEN,
            **kwargs,
        )

    @staticmethod
    def unauthorized(
        message: str = "Authentication required",
        error_code: str = "AUTHENTICATION_REQUIRED",
        **kwargs,
    ) -> Response:
        return APIResponse.error(
            message,
            error_code=error_code,
            status_code=status.HTTP_401_UNAUTHORIZED,
            **kwargs,
        )

    @staticmethod
    def validation_error(
        errors: Dict,
        message: str = "Validation failed",
        error_code: str = "VALIDATION_ERROR",
        **kwargs,
    ) -> Response:
        return APIResponse.error(
            message, errors, error_code, status.HTTP_400_BAD_REQUEST, **kwargs
        )

    @staticmethod
    def server_error(
        message: str = "Internal server error",
        error_code: str = "INTERNAL_SERVER_ERROR",
        **kwargs,
    ) -> Response:
        return APIResponse.error(
            message,
            error_code=error_code,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            **kwargs,
        )
