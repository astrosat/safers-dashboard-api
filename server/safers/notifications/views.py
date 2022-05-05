from copy import deepcopy

from django.conf import settings
from django.contrib.gis.geos import Polygon
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_filters import rest_framework as filters

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from safers.core.filters import DefaultFilterSetMixin, SwaggerFilterInspector

from safers.users.permissions import IsRemote

from safers.notifications.models import Notification, NotificationGeometry
from safers.notifications.serializers import NotificationSerializer


_notification_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    example={
        "id": "db9634fc-ae64-44bf-ba31-7abf4f68daa9",
        "timestamp": "2022-04-28T11:38:28Z",
        "status": "Actual",
        "source": "EFFIS_FWI",
        "scope": "Public",
        "category": "Met",
        "event": "Probability of fire",
        "urgency": "Immediate",
        "severity": "Extreme",
        "certainty": "Likely",
        "description": "Do not light open-air barbecues in forest.",
        "geometry": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [1, 2],
                            [3, 4]
                        ]
                    },
                    "properties": {
                        "description": "areaDesc"
                    }
                }
            ]
        },
        "center": [1, 2],
        "bounding_box": [1, 2, 3, 4]
    }
)  # yapf: disable


_notification_list_schema = openapi.Schema(
    type=openapi.TYPE_ARRAY, items=_notification_schema
)


class NotificationFilterSet(DefaultFilterSetMixin, filters.FilterSet):
    class Meta:
        model = Notification
        fields = {
            "status",
            "source",
            "scope",
            "category",
            "event",
            "urgency",
            "severity",
            "certainty",
        }

    start_date = filters.DateTimeFilter(
        field_name="timestamp", lookup_expr="date__gte"
    )
    end_date = filters.DateTimeFilter(
        field_name="timestamp", lookup_expr="date__lte"
    )
    default_date = filters.BooleanFilter(
        initial=True,
        help_text=_(
            "If default_date is True and no end_date is provided then the current date will be used and if no start_date is provided then 3 days previous will be used; "
            "If default_date is False and no end_date or start_date is used then no date filters will be passed to the API."
        )
    )
    bbox = filters.Filter(
        method="bbox_method", help_text=_("xmin, ymin, xmax, ymax")
    )
    default_bbox = filters.BooleanFilter(
        initial=True,
        help_text=_(
            "If default_bbox is True and no bbox is provided the user's default_aoi bbox will be used; "
            "If default_bbox is False and no bbox is provided then no bbox filter will be passed to the API"
        )
    )

    def bbox_method(self, queryset, name, value):

        try:
            xmin, ymin, xmax, ymax = list(map(float, value.split(",")))
        except ValueError:
            raise ParseError("invalid bbox string supplied")
        bbox = Polygon.from_bbox((xmin, ymin, xmax, ymax))

        return queryset.filter(geometries__geometry__intersects=bbox)

    def filter_queryset(self, queryset):
        """
        As per the documentation, I am overriding this method in order to perform
        additional filtering to the queryset before it is cached
        """

        # update filters based on default values

        updated_cleaned_data = deepcopy(self.form.cleaned_data)

        default_bbox = updated_cleaned_data.pop("default_bbox")
        if default_bbox and not updated_cleaned_data.get("bbox"):
            user = self.request.user
            bbox = user.default_aoi.geometry.extent
            updated_cleaned_data["bbox"] = ",".join(map(str, bbox))

        default_date = updated_cleaned_data.pop("default_date")
        if default_date and not updated_cleaned_data.get("end_date"):
            updated_cleaned_data["end_date"] = timezone.now()
        if default_date and not updated_cleaned_data.get("start_date"):
            updated_cleaned_data["start_date"] = timezone.now(
            ) - settings.SAFERS_DEFAULT_TIMERANGE

        self.form.cleaned_data = updated_cleaned_data

        return super().filter_queryset(queryset)


@method_decorator(
    swagger_auto_schema(
        responses={status.HTTP_200_OK: _notification_list_schema},
        filter_inspectors=[SwaggerFilterInspector]
    ),
    name="list",
)
@method_decorator(
    swagger_auto_schema(
        responses={status.HTTP_200_OK: _notification_list_schema},
    ),
    name="retrieve",
)
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):

    filter_backends = (filters.DjangoFilterBackend, )
    filterset_class = NotificationFilterSet

    lookup_field = "id"
    lookup_url_kwarg = "notification_id"
    permission_classes = [IsAuthenticated, IsRemote]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        queryset = Notification.objects.all()
        return queryset.prefetch_related("geometries")

    # @action(detail=True, methods=["post"])
    # def favorite(self, request, **kwargs):
    #     """
    #     Toggles the favorite status of the specified object
    #     """
    #     user = request.user
    #     obj = self.get_object()

    #     if obj not in user.favorite_notifications.all():
    #         max_favorites = settings.SAFERS_MAX_NOTIFICATIONS
    #         if user.favorite_notifications.count() >= max_favorites:
    #             raise ValidationError(
    #                 f"cannot have more than {max_favorites} notifications."
    #             )
    #         user.favorite_notifications.add(obj)
    #     else:
    #         user.favorite_notifications.remove(obj)

    #     SerializerClass = self.get_serializer_class()
    #     serializer = SerializerClass(obj, context=self.get_serializer_context())

    #     return Response(serializer.data, status=status.HTTP_200_OK)
