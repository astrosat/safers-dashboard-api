from collections import defaultdict

from django.conf import settings

from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from drf_yasg.utils import swagger_serializer_method

from safers.aois.models import Aoi

from safers.alerts.models import Alert

from safers.events.models import Event

from safers.cameras.models import CameraMedia

from safers.users.models import User
from safers.users.serializers import Oauth2UserSerializer


class UserSerializerLite(serializers.ModelSerializer):
    """
    A "lite" serializer just for some high-level user details
    (can be used by LoginView & RegisterView)
    """
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "accepted_terms",
            "is_verified",
            "last_login",
            "is_local",
            "is_remote",
            "is_professional",
            "is_citizen",
        )

    last_login = serializers.DateTimeField(read_only=True)

    @swagger_serializer_method(serializer_or_field=serializers.BooleanField)
    def is_verified(self, obj):
        return obj.is_verified


class UserSerializer(UserSerializerLite):
    """
    The "real" User Serializer; used for CRUD operations
    """
    class Meta:
        model = User
        fields = UserSerializerLite.Meta.fields + (
            "organization_name",
            "role_name",
            "organization",
            "role",
            "profile",
            "default_aoi",
            "oauth2",
        )

    organization_name = serializers.CharField(
        required=False,
        write_only=True,
    )

    role_name = serializers.CharField(
        required=False,
        write_only=True,
    )

    organization = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
    )

    role = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
    )
    default_aoi = serializers.PrimaryKeyRelatedField(
        queryset=Aoi.objects.active(), required=False, allow_null=True
    )

    oauth2 = Oauth2UserSerializer(source="auth_user")

    def validate(self, data):
        validated_data = super().validate(data)
        organization = validated_data.get("organization")
        role = validated_data.get("role")
        if organization and role and role.name == "citizen":
            raise serializers.ValidationError(
                "A citizen must not belong to an organization."
            )
        return validated_data

    def validate_username(self, value):
        if value in settings.ACCOUNT_USERNAME_BLACKLIST:
            raise serializers.ValidationError(
                f"{value} is not an allowed username"
            )
        return value


class ReadOnlyUserSerializer(UserSerializer):
    """
    A serializer that doesn't allow modifying organization or role
    """
    class Meta:
        model = User
        fields = UserSerializer.Meta.fields
