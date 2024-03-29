from copy import deepcopy

from django.conf import settings
from django.contrib.gis.geos import Polygon
from django.db.models import BooleanField, ExpressionWrapper, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.generics import get_object_or_404 as drf_get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django_filters import rest_framework as filters

from drf_spectacular.utils import extend_schema, extend_schema_field, OpenApiExample, OpenApiResponse, OpenApiTypes

from safers.core.decorators import swagger_fake
from safers.core.filters import CaseInsensitiveChoiceFilter, DefaultFilterSetMixin, MultiFieldOrderingFilter

from safers.alerts.models import Alert, AlertType, AlertSource
from safers.alerts.serializers import AlertViewSetSerializer


class AlertFilterSet(DefaultFilterSetMixin, filters.FilterSet):
    class Meta:
        model = Alert
        fields = {
            "type",
            "status",
            "source",
            "scope",
            "category",
            "urgency",
            "severity",
            "certainty",
        }

    type = filters.ChoiceFilter(choices=AlertType.choices)

    source = CaseInsensitiveChoiceFilter(choices=AlertSource.choices)

    order = MultiFieldOrderingFilter(
        fields=(("timestamp", "date"), ), multi_fields=["-favorite"]
    )

    start_date = filters.DateFilter(
        field_name="timestamp", lookup_expr="date__gte"
    )
    end_date = filters.DateFilter(
        field_name="timestamp", lookup_expr="date__lte"
    )
    default_date = filters.BooleanFilter(
        initial=False,
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

    @extend_schema_field(OpenApiTypes.STR)
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

        # update filters based on default fields

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


class AlertViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):

    filter_backends = (filters.DjangoFilterBackend, )
    filterset_class = AlertFilterSet

    lookup_field = "id"
    lookup_url_kwarg = "alert_id"
    permission_classes = [IsAuthenticated]
    serializer_class = AlertViewSetSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # run this query once in the view instead of N times in the serializer
        context["favorite_alert_ids"
               ] = self.request.user.favorite_alerts.values_list(
                   "id", flat=True
               )
        return context

    @swagger_fake(Alert.objects.none())
    def get_queryset(self):
        """
        ensures that favorite alerts are at the start of the qs
        """
        user = self.request.user
        favorite_alert_ids = user.favorite_alerts.values_list("id", flat=True)

        qs = Alert.objects.all().select_related("country").prefetch_related(
            "geometries",
            "camera_media",
        )

        qs = qs.annotate(
            favorite=ExpressionWrapper(
                Q(id__in=favorite_alert_ids),
                output_field=BooleanField(),
            )
        )
        return qs.order_by("-favorite")

    def get_object(self):
        queryset = self.get_queryset()

        # disable filtering for detail views
        # (the rest of this fn is just like the parent class)
        # TODO: https://github.com/astrosat/safers-dashboard-api/issues/45
        if self.action in ["list"]:
            queryset = self.filter_queryset(queryset)

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = drf_get_object_or_404(queryset, **filter_kwargs)

        self.check_object_permissions(self.request, obj)

        return obj

    @extend_schema(
        responses={
            status.HTTP_200_OK:
                OpenApiResponse(
                    OpenApiTypes.OBJECT,
                    examples=[
                        OpenApiExample(
                            "valid responese",
                            {
                                "detail":
                                    "added alert <name> to existing event: <id>"
                            }
                        )
                    ]
                ),
            status.HTTP_201_CREATED:
                OpenApiResponse(
                    OpenApiTypes.OBJECT,
                    examples=[
                        OpenApiExample(
                            "valid response",
                            {"detail": "added alert <name> to new event: <id>"}
                        )
                    ]
                ),
        },
        request=None,
    )
    @action(detail=True, methods=["post"])
    def validate(self, request, **kwargs):
        """
        Sets an alert's type from 'unvalidated' to 'validated' and updates the set of events accordingly.
        """
        obj = self.get_object()

        if obj.type == AlertType.VALIDATED:
            raise ValidationError(f"{obj.title} is already validated")

        event, created = obj.validate()
        if created:
            response_status = status.HTTP_201_CREATED
            response_data = f"added {obj.title} to new event: {event}"
        else:
            response_status = status.HTTP_200_OK
            response_data = f"added {obj.title} to existing event: {event}"

        return Response({"detail": response_data}, status=response_status)

    @extend_schema(request=None)
    @action(detail=True, methods=["post"])
    def favorite(self, request, **kwargs):
        """
        Toggles the favorite status of the specified object
        """
        user = request.user
        obj = self.get_object()

        if obj not in user.favorite_alerts.all():
            max_favorites = settings.SAFERS_MAX_FAVORITE_ALERTS
            if user.favorite_alerts.count() >= max_favorites:
                raise ValidationError(
                    f"cannot have more than {max_favorites} alerts."
                )
            user.favorite_alerts.add(obj)
        else:
            user.favorite_alerts.remove(obj)

        SerializerClass = self.get_serializer_class()
        serializer = SerializerClass(obj, context=self.get_serializer_context())

        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    request=None,
    responses={
        status.HTTP_200_OK:
            OpenApiResponse(
                OpenApiTypes.ANY,
                examples=[OpenApiExample("valid response", ["string"])]
            ),
    }
)
@api_view(["GET"])
@permission_classes([AllowAny])
def alert_sources_view(request):
    """
    Returns the list of possible alert sources.
    """
    return Response(AlertSource.values, status=status.HTTP_200_OK)
