from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate registration data and create a user."""

    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True, trim_whitespace=False
    )
    confirmed_password = serializers.CharField(
        write_only=True, trim_whitespace=False
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "confirmed_password",
        ]

    def validate_email(self, value):
        """Check whether the email is already registered."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Email is already registered."
            )
        return value

    def validate(self, attrs):
        """Validate passwords."""
        if attrs["password"] != attrs["confirmed_password"]:
            raise serializers.ValidationError(
                {"confirmed_password": "Passwords do not match."}
            )
        user = User(
            username=attrs["username"], email=attrs["email"]
        )
        validate_password(attrs["password"], user=user)
        return attrs

    def create(self, validated_data):
        """Create a user with a hashed password."""
        validated_data.pop("confirmed_password")
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Validate login credentials."""

    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True, trim_whitespace=False
    )