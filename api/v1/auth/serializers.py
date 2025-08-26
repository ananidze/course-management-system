from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from users.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "role",
            "gender",
        ]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "role": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, style={"input_type": "password"})

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password
            )
            if not user:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials."
                )
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
        else:
            raise serializers.ValidationError('Must include "email" and "password".')

        attrs["user"] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)
    is_teacher = serializers.BooleanField(read_only=True)
    is_student = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "gender",
            "is_teacher",
            "is_student",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "gender",
        ]


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(
        required=False, help_text="Refresh token to blacklist"
    )


# Response serializers for Swagger documentation
class TokenSerializer(serializers.Serializer):
    access = serializers.CharField(help_text="JWT access token")
    refresh = serializers.CharField(help_text="JWT refresh token")


class LoginResponseSerializer(serializers.Serializer):
    tokens = TokenSerializer()
    user = UserProfileSerializer()


class RegistrationResponseSerializer(serializers.Serializer):
    user = UserProfileSerializer()


class APIResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(
        help_text="Indicates if the operation was successful"
    )
    message = serializers.CharField(help_text="Response message")
    data = serializers.JSONField(help_text="Response data", required=False)


class LoginAPIResponseSerializer(APIResponseSerializer):
    data = LoginResponseSerializer(help_text="Login response data")


class RegistrationAPIResponseSerializer(APIResponseSerializer):
    data = RegistrationResponseSerializer(help_text="Registration response data")


class UserProfileAPIResponseSerializer(APIResponseSerializer):
    data = UserProfileSerializer(help_text="User profile data")
