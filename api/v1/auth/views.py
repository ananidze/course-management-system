from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from django.contrib.auth import logout

from api.core.responses import APIResponse
from api.core.documentation import CommonResponses
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    LogoutSerializer,
    LoginAPIResponseSerializer,
    RegistrationAPIResponseSerializer,
    UserProfileAPIResponseSerializer,
)


@extend_schema(
    summary="User Registration",
    description="Register a new user account with email, password, and role selection",
    request=UserRegistrationSerializer,
    responses={
        201: RegistrationAPIResponseSerializer,
        400: CommonResponses.VALIDATION_ERROR,
    },
    tags=["auth"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def user_registration(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        return APIResponse.created(
            data={
                "user": UserProfileSerializer(user).data,
            },
            message="User registered successfully",
        )
    return APIResponse.validation_error(serializer.errors)


@extend_schema(
    summary="User Login",
    description=(
        "Authenticate user with email and password, return JWT tokens and user profile"
    ),
    request=UserLoginSerializer,
    responses={
        200: LoginAPIResponseSerializer,
        400: CommonResponses.VALIDATION_ERROR,
    },
    tags=["auth"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def user_login(request):
    serializer = UserLoginSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return APIResponse.success(
            data={
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                "user": UserProfileSerializer(user).data,
            },
            message="Login successful",
        )
    return APIResponse.validation_error(serializer.errors)


@extend_schema(
    summary="User Logout",
    description="Logout user and blacklist refresh token for security",
    request=LogoutSerializer,
    responses={
        200: CommonResponses.SUCCESS_RESPONSE,
    },
    tags=["auth"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_logout(request):
    try:
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        logout(request)
        return APIResponse.success(message="Logout successful")
    except Exception:
        return APIResponse.success(message="Logout successful")


@extend_schema(
    summary="Get Current User",
    description="Retrieve the profile of the currently authenticated user",
    responses={
        200: UserProfileAPIResponseSerializer,
        401: CommonResponses.UNAUTHORIZED,
    },
    tags=["auth"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    serializer = UserProfileSerializer(request.user)
    return APIResponse.success(
        data=serializer.data, message="User profile retrieved successfully"
    )
