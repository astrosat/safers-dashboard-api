from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from drf_spectacular.utils import extend_schema_serializer


@extend_schema_serializer(exclude_fields=["include_map_requests", "n_layers"])
class OperationalLayerViewSerializer(serializers.Serializer):
    OrderType = models.TextChoices("OrderType", "date -date")

    order = serializers.ChoiceField(choices=OrderType.choices, required=False)

    # REMOVED TIMESTAMP/BBOX FILTERING AS PER https://astrosat.atlassian.net/browse/SAFB-255
    # bbox
    # start
    # end

    include_map_requests = serializers.BooleanField(
        source="IncludeMapRequests",
        default=False,
        required=False,
        help_text=_(
            "Whether or not to include on-demand MapRequests.  "
            "This ought to be 'False' to distinguish operational from on-demand layers."
        ),
    )

    n_layers = serializers.IntegerField(
        default=1,
        required=False,
        help_text=_(
            "The number of recent layers to return for each data type. "
            "It is very unlikely you want to change this value."
        ),
    )

    def validate_n_layers(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "n_layers must be greater than 0."
            )
        return value
