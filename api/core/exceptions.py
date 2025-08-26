from rest_framework.views import exception_handler
from rest_framework import status
from django.core.exceptions import ValidationError
from django.http import Http404
import logging

from .responses import APIResponse

logger = logging.getLogger(__name__)


class APIException(Exception):
    def __init__(self, message=None, error_code=None, status_code=None, errors=None):
        self.message = message or "An error occurred"
        self.error_code = error_code or "API_ERROR"
        self.status_code = status_code or status.HTTP_400_BAD_REQUEST
        self.errors = errors
        super().__init__(self.message)


class ResourceNotFoundException(APIException):
    def __init__(self, message=None, resource_type=None):
        message = message or f"{resource_type or 'Resource'} not found"
        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class PermissionDeniedException(APIException):
    def __init__(self, message=None):
        message = message or "You don't have permission to perform this action"
        super().__init__(
            message=message,
            error_code="PERMISSION_DENIED",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ValidationException(APIException):
    def __init__(self, message=None, errors=None):
        message = message or "Validation failed"
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=errors,
        )


class BusinessLogicException(APIException):
    def __init__(self, message=None, error_code=None):
        super().__init__(
            message=message or "Business logic error",
            error_code=error_code or "BUSINESS_LOGIC_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if hasattr(exc, "detail"):
            if isinstance(exc.detail, dict):
                errors = exc.detail
                message = "Validation failed"
            else:
                errors = None
                message = str(exc.detail)
        else:
            errors = None
            message = str(exc)

        logger.error(f"API Exception: {message}", exc_info=True)

        return APIResponse.error(
            message=message,
            errors=errors,
            error_code=getattr(exc, "error_code", "API_ERROR"),
            status_code=response.status_code,
        )

    if isinstance(exc, APIException):
        logger.error(f"Custom API Exception: {exc.message}", exc_info=True)
        return APIResponse.error(
            message=exc.message,
            errors=exc.errors,
            error_code=exc.error_code,
            status_code=exc.status_code,
        )

    if isinstance(exc, Http404):
        logger.warning(f"Resource not found: {exc}")
        return APIResponse.not_found("Resource not found")

    if isinstance(exc, ValidationError):
        logger.warning(f"Validation error: {exc}")
        errors = (
            exc.message_dict
            if hasattr(exc, "message_dict")
            else {"detail": exc.messages}
        )
        return APIResponse.validation_error(errors)

    logger.error(f"Unexpected exception: {exc}", exc_info=True)
    return APIResponse.server_error()


def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIException as e:
            return APIResponse.error(
                message=e.message,
                errors=e.errors,
                error_code=e.error_code,
                status_code=e.status_code,
            )
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            return APIResponse.server_error()

    return wrapper
