from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers, ISO_8601
from rest_framework_gis import serializers as gis_serializers

from safers.core.fields import UnderspecifiedDateTimeField
from safers.core.serializers import ContextVariableDefault

DataLayerSerializerDateTimeFormats = [
    ISO_8601, "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"
]

## REMOVED TIMESTAMP/BBOX FILTERING AS PER https://astrosat.atlassian.net/browse/SAFB-255
## THIS CLASS IS NO LONGER USED BY DataLayerViewSerializer


class DataViewSerializer(serializers.Serializer):
    """
    Note that this isn't a ModelSerializer; it's just being
    used for query_param validation in the DataLayer Views
    """

    OrderType = models.TextChoices("OrderType", "date -date")
    ProxyFieldMapping = {
        # fields to pass onto proxy
        "bbox": "Bbox",
        "start": "Start",
        "end": "End",
        "include_map_requests": "IncludeMapRequests",
    }

    n_layers = serializers.IntegerField(
        default=1,
        required=False,
        help_text=_(
            "The number of recent layers to return for each data type. "
            "It is very unlikely you want to change this value."
        ),
    )

    bbox = serializers.CharField(required=False)

    start = UnderspecifiedDateTimeField(
        input_formats=DataLayerSerializerDateTimeFormats,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        required=False,
    )

    end = UnderspecifiedDateTimeField(
        input_formats=DataLayerSerializerDateTimeFormats,
        hour=23,
        minute=59,
        second=59,
        microsecond=999999,
        required=False,
    )

    order = serializers.ChoiceField(choices=OrderType.choices, required=False)

    default_date = serializers.BooleanField(
        default=False,
        required=False,
        help_text=_(
            "If default_date is True and no start/end is provided the default start/end (now / 3 days prior) will be used; "
            "If default_date is False and no start/end is provided then no start/end filters will be passed to the API"
        )
    )

    default_bbox = serializers.BooleanField(
        default=True,
        required=False,
        help_text=_(
            "If default_bbox is True and no bbox is provided the user's default_aoi bbox will be used; "
            "If default_bbox is False and no bbox is provided then no bbox filter will be passed to the API"
        )
    )

    def validate_n_layers(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "n_layers must be greater thann 0."
            )
        return value

    def validate_bbox(self, value):
        try:
            bbox = list(map(float, value.split(",")))
            assert len(bbox) == 4, "bbox must contain 4 values"
        except Exception as e:
            raise serializers.ValidationError(e)
        return bbox

    def validate(self, data):

        validated_data = super().validate(data)

        # check timestamps...
        start = validated_data.get("start")
        end = validated_data.get("end")
        if start and end and start >= end:
            raise serializers.ValidationError("end must occur after start")

        return validated_data
