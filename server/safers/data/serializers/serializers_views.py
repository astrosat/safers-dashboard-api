from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from safers.core.fields import EmptyBooleanField
from safers.core.serializers import ContextVariableDefault


class LayerViewSerializer(serializers.Serializer):
    OrderType = models.TextChoices("OrderType", "date -date")

    order = serializers.ChoiceField(choices=OrderType.choices, required=False)

    # REMOVED TIMESTAMP/BBOX FILTERING AS PER https://astrosat.atlassian.net/browse/SAFB-255
    # bbox
    # start
    # end

    include_map_requests = EmptyBooleanField(
        source="IncludeMapRequests",
        default=ContextVariableDefault(
            "include_map_requests", raise_error=True
        ),
        help_text=_(
            "Whether or not to include on-demand MapRequests.  "
            "This ought to be 'False' to distinguish operational from on-demand layers."
        ),
    )

    map_request_codes = serializers.ListField(
        # using a ListField b/c the gateway API adds multiple query_params to the request
        # ie: `&MapRequestCodes=1&MapRequestCodes=2` instead of `&MapRequestCodes=1,2`
        source="MapRequestCodes",
        default=ContextVariableDefault("map_request_codes", raise_error=False),
        required=False,
        help_text=_(
            "The request_ids to include in the query.  "
            "There is no need to provide a value to the request, as it is autogenerated."
        )
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

    def validate(self, data):
        validated_data = super().validate(data)
        if not validated_data["IncludeMapRequests"] and validated_data.get(
            "MapRequestCodes"
        ):
            raise serializers.ValidationError(
                "If you provide map_request_codes, then include_map_requests must be true."
            )
        return validated_data