from copy import deepcopy

from django.conf import settings
from django.contrib.gis.geos import Polygon
from django.db.models import BooleanField, ExpressionWrapper, Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.generics import get_object_or_404 as drf_get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_filters import rest_framework as filters

from drf_spectacular.utils import extend_schema, extend_schema_field, OpenApiTypes

from safers.core.decorators import swagger_fake
from safers.core.filters import DefaultFilterSetMixin, MultiFieldOrderingFilter

from safers.events.models import Event, EventStatusChoices
from safers.events.serializers import EventSerializer

###########
# filters #
###########


class EventFilterSet(DefaultFilterSetMixin, filters.FilterSet):
    class Meta:
        model = Event
        fields = {}

    order = MultiFieldOrderingFilter(
        fields=(("start_date", "date"), ), multi_fields=["-favorite"]
    )

    status = filters.MultipleChoiceFilter(
        method="status_method",
        choices=EventStatusChoices.choices,
        conjoined=True,
    )

    start_date = filters.DateFilter(
        field_name="start_date", lookup_expr="date__gte"
    )
    end_date = filters.DateFilter(
        field_name="start_date", lookup_expr="date__lte"
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

    def status_method(self, queryset, name, values):
        filter_kwargs = {
            # if end_date is None then the status must be ONGOING
            # if end_date is not None then the status must be CLOSED
            "end_date__isnull": value == EventStatusChoices.ONGOING
            for value in values
        }
        return queryset.filter(**filter_kwargs)

    @extend_schema_field(OpenApiTypes.STR)
    def bbox_method(self, queryset, name, value):

        try:
            xmin, ymin, xmax, ymax = list(map(float, value.split(",")))
        except ValueError:
            raise ParseError("invalid bbox string supplied")
        bbox = Polygon.from_bbox((xmin, ymin, xmax, ymax))

        return queryset.filter(geometry_collection__intersects=bbox)

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


#########
# views #
#########


class EventViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    filter_backends = (filters.DjangoFilterBackend, )
    filterset_class = EventFilterSet

    lookup_field = "id"
    lookup_url_kwarg = "event_id"
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer

    @swagger_fake(Event.objects.none())
    def get_queryset(self):
        """
        ensures that favorite events are at the start of the qs
        """
        user = self.request.user
        favorite_event_ids = user.favorite_events.values_list("id", flat=True)

        qs = Event.objects.all()
        qs = qs.annotate(
            favorite=ExpressionWrapper(
                Q(id__in=favorite_event_ids),
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

    @extend_schema(request=None)
    @action(detail=True, methods=["post"])
    def favorite(self, request, **kwargs):
        """
        Toggles the favorite status of the specified object
        """
        user = request.user
        obj = self.get_object()

        if obj not in user.favorite_events.all():
            max_favorites = settings.SAFERS_MAX_FAVORITE_EVENTS
            if user.favorite_events.count() >= max_favorites:
                raise ValidationError(
                    f"cannot have more than {max_favorites} events."
                )
            user.favorite_events.add(obj)
        else:
            user.favorite_events.remove(obj)

        SerializerClass = self.get_serializer_class()
        serializer = SerializerClass(obj, context=self.get_serializer_context())

        return Response(serializer.data, status=status.HTTP_200_OK)
