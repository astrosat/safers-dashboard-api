import json
import re
import uuid

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from rest_framework.utils.encoders import JSONEncoder

from sequences import Sequence

from safers.data.models import DataType

from safers.rmq import RMQ, RMQ_USER
from safers.rmq.exceptions import RMQException

###########
# helpers #
###########

REQUEST_ID_GENERATOR = Sequence("map_requests")

REQUEST_ID_SEPARATOR = "-"

REQUEST_ROUTING_KEY_REGEX = re.compile(
    f"status\.(\w+)\.(\d+)\.{RMQ_USER}\.(.+)"
)


def get_next_request_id():
    with transaction.atomic():
        next_request_id = next(REQUEST_ID_GENERATOR)
        try:
            current_site_code = get_current_site(None).profile.code
            if current_site_code:
                next_request_id = f"{current_site_code}{REQUEST_ID_SEPARATOR}{next_request_id}"
        except ObjectDoesNotExist:
            # SiteProfile _might_ not exist during tests
            pass

        return f"{next_request_id}"


class MapRequestStatus(models.TextChoices):
    PROCESSING = "PROCESSING", _("Processing")
    FAILED = "FAILED", _("Failed")
    AVAILABLE = "AVAILABLE", _("Available")


##################
# managers, etc. #
##################


class MapRequestManager(models.Manager):
    pass


class MapRequestQuerySet(models.QuerySet):
    def any_layers_processing(self):
        return self.filter(
            Q(map_request_data_types__status=MapRequestStatus.PROCESSING),
        ).distinct()

    def any_layers_failed(self):
        return self.filter(
            Q(map_request_data_types__status=MapRequestStatus.FAILED),
        ).distinct()

    def any_layers_available(self):
        return self.filter(
            Q(map_request_data_types__status=MapRequestStatus.AVAILABLE),
        ).distinct()

    def any_layers_none(self):
        return self.filter(Q(map_request_data_types__status__is_null=True
                            ), ).distinct()

    def none_layers_processing(self):
        return self.filter(
            ~Q(map_request_data_types__status=MapRequestStatus.PROCESSING),
        ).distinct()

    def none_layers_failed(self):
        return self.filter(
            ~Q(map_request_data_types__status=MapRequestStatus.FAILED),
        ).distinct()

    def none_layers_available(self):
        return self.filter(
            ~Q(map_request_data_types__status=MapRequestStatus.AVAILABLE),
        ).distinct()

    def none_layers_none(self):
        return self.filter(~Q(map_request_data_types__status__isnull=True
                             ), ).distinct()

    def all_layers_processing(self):
        return self.filter(
            Q(map_request_data_types__status=MapRequestStatus.PROCESSING),
            ~Q(map_request_data_types__status=MapRequestStatus.FAILED),
            ~Q(map_request_data_types__status=MapRequestStatus.AVAILABLE),
            ~Q(map_request_data_types__status__isnull=True),
        ).distinct()

    def all_layers_failed(self):
        return self.filter(
            Q(map_request_data_types__status=MapRequestStatus.FAILED),
            ~Q(map_request_data_types__status=MapRequestStatus.PROCESSING),
            ~Q(map_request_data_types__status=MapRequestStatus.AVAILABLE),
            ~Q(map_request_data_types__status__isnull=True),
        ).distinct()

    def all_layers_available(self):
        return self.filter(
            Q(map_request_data_types__status=MapRequestStatus.AVAILABLE),
            ~Q(map_request_data_types__status=MapRequestStatus.PROCESSING),
            ~Q(map_request_data_types__status=MapRequestStatus.FAILED),
            ~Q(map_request_data_types__status__isnull=True),
        ).distinct()

    def all_layers_none(self):
        return self.filter(
            Q(map_request_data_types__status__isnull=True),
            ~Q(map_request_data_types__status=MapRequestStatus.PROCESSING),
            ~Q(map_request_data_types__status=MapRequestStatus.FAILED),
            ~Q(map_request_data_types__status=MapRequestStatus.AVAILABLE),
        ).distinct()


###########
# models #
##########


class MapRequest(gis_models.Model):
    class Meta:
        verbose_name = "Map Request"
        verbose_name_plural = "Map Reqeusts"

    PRECISION = 12

    objects = MapRequestManager.from_queryset(MapRequestQuerySet)()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    request_id = models.CharField(
        max_length=255,
        # default=get_next_request_id  (cannot use generator as default as per https://code.djangoproject.com/ticket/11390 )
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="map_requests",
        help_text=_("User that issued the MapRequest")
    )

    title = models.CharField(max_length=255)

    data_types = models.ManyToManyField(
        DataType,
        related_name="map_requests",
        through="MapRequestDataType",
    )

    parameters = models.JSONField(blank=True, default=dict)

    geometry = gis_models.GeometryField(
        blank=True, null=True
    )  # TODO: CAN THIS BE A GeometryCollectionField

    geometry_wkt = models.TextField(
        blank=True, null=True, help_text=_("WKT representation of geometry")
    )

    def save(self, *args, **kwargs):
        """
        automatically set the request_id & geometry_wkt when saving
        """
        if not self.request_id:
            self.request_id = get_next_request_id()

        if not self.geometry:
            self.geometry_wkt = None
        else:
            self.geometry_wkt = self.geometry.wkt

        return super().save(*args, **kwargs)

    ###################
    # RMQ interaction #
    ###################

    def invoke(self):
        """
        publish a message to RMQ in order to trigger the creation of this MapRequest's data
        (called from MapRequestViewSet.perform_create)
        """
        rmq = RMQ()

        message_body = self.parameters
        if self.geometry:
            message_body["geometry"] = json.loads(self.geometry.geojson)

        try:

            for data_type in self.data_types.all():
                routing_key = f"request.{data_type.datatype_id}.{RMQ_USER}.{self.request_id}"

                message_body["datatype_id"] = data_type.datatype_id

                rmq.publish(
                    json.dumps(message_body, cls=JSONEncoder),
                    routing_key,
                    # str(self.id),
                    self.request_id,
                )

        except Exception as e:
            msg = f"unable to publish message: {e}"
            raise RMQException(msg)

    def revoke(self):
        """
        publish a message to RMQ in order to trigger the destruction of this MapRequest's data
        (called from MapRequestViewSet.perform_destroy)
        """

        raise NotImplementedError("Unable to delete MapRequest Data")

    @classmethod
    def process_message(cls, message_body, **kwargs):

        method = kwargs.get("method", None)
        properties = kwargs.get("properties", {})

        try:
            routing_key = method.routing_key
            (
                app_id,
                datatype_id,
                request_id,
            ) = re.match(REQUEST_ROUTING_KEY_REGEX, routing_key).groups()

            with transaction.atomic():
                data_type = DataType.objects.get(datatype_id=datatype_id)
                map_request = MapRequest.objects.get(request_id=request_id)
                map_request_data_type = MapRequestDataType(
                    data_type=data_type, map_request=map_request
                )
                # assert data_type in map_request.data_types.all()

                message_type = message_body.get("type")
                if map_request_data_type == "start":
                    map_request.status = MapRequestStatus.PROCESSING
                elif message_type == "end":
                    map_request_data_type.status = MapRequestStatus.AVAILABLE

                if message_body.get("status_code") != 200:
                    map_request_data_type.status = MapRequestStatus.FAILED

                map_request_data_type.save()

        except Exception as e:
            msg = f"unable to process message: {e}"
            raise RMQException(msg)


class MapRequestDataType(models.Model):
    """
    a "through" model to add some extra fields to the relationship betweeen a DataType and a MapRequest
    """

    map_request = models.ForeignKey(
        MapRequest,
        on_delete=models.CASCADE,
        related_name="map_request_data_types"
    )
    data_type = models.ForeignKey(
        DataType,
        on_delete=models.CASCADE,
        related_name="map_request_data_types"
    )

    url = models.CharField(max_length=512, blank=True, null=True)
    status = models.CharField(
        max_length=64,
        choices=MapRequestStatus.choices,
        blank=True,
        null=True,
    )