from rest_framework import serializers
from rest_framework_gis import serializers as gis_serializers

from safers.alerts.models import Alert


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = (
            "id",
            "timestamp",
            "description",
            "source",
            "status",
            "media",
            "geometry",
            "bounding_box",
            "favorite",
        )

    geometry = gis_serializers.GeometryField(
        precision=Alert.PRECISION, remove_duplicates=True
    )
    bounding_box = gis_serializers.GeometryField(precision=Alert.PRECISION)

    favorite = serializers.SerializerMethodField(method_name="is_favorite")

    def is_favorite(self, obj):
        user = self.context["request"].user
        return obj in user.favorite_alerts.all()