from rest_framework import serializers
from rest_framework_gis import serializers as gis_serializers

from safers.social.models import Tweet


class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = (
            "id",
            "external_id",
            "type",
            "category",
            "start_date",
            "end_date",
            "geometry",
            "bounding_box",
        )  # yapf: disable

    geometry = gis_serializers.GeometryField(
        precision=Tweet.PRECISION, remove_duplicates=True
    )
    bounding_box = gis_serializers.GeometryField(precision=Tweet.PRECISION)
