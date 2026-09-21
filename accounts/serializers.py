from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User


class BaseUserSerializer(serializers.ModelSerializer):
    """Base serializer containing common user fields."""

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class UserSerializer(BaseUserSerializer):
    """Serializer for displaying and updating a user."""

    full_name = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + [
            "full_name",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def update(self, instance, validated_data):
        """Update user profile."""
        validated_data.pop("role", None)

        return super().update(
            instance,
            validated_data,
        )


class UserRegistrationSerializer(
    BaseUserSerializer
):
    """Serializer used when registering a new user."""

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + [
            "password",
            "password_confirm",
        ]

    def validate_email(self, value):
        """Ensure email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return value

    def validate(self, data):
        """Ensure passwords match."""
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {
                    "password_confirm":
                    "Passwords do not match."
                }
            )

        return data

    def create(self, validated_data):
        """Create a user with a hashed password."""
        validated_data.pop("password_confirm")

        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data,
        )

        return user


class LoginSerializer(serializers.Serializer):
    """Validate login credentials."""

    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True
    )

    def validate(self, data):
        """Authenticate the supplied credentials."""
        user = authenticate(
            username=data["username"],
            password=data["password"],
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid username or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This account is inactive."
            )

        data["user"] = user

        return data