import uuid

from django.contrib.gis import geos
from django.db import models, transaction
from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _

from safers.core.mixins import HashableMixin
from safers.rmq.exceptions import RMQException


class AlertType(models.TextChoices):
    UNVALIDATED = "UNVALIDATED", _("Unvalidated")
    VALIDATED = "VALIDATED", _("Validated")
    POSSIBLE_EVENT = "POSSIBLE_EVENT", _("Possible Event")


class AlertManager(models.Manager):
    pass


class AlertQuerySet(models.QuerySet):
    def filter_by_distance(self, target, distance=None):
        return self.filter()

    def filter_by_time(self, target, time=None):
        return self.filter()


# TODO: ALERTS COME FROM...
# TODO: 1. Semantic Reasoning Module (CERTH)
# TODO: 2. IN-SITU CAMERAS (WATERVIEW)
# TODO: 3. "ELIOTSHUB" (https://alert-hub.s3.amazonaws.com/cap-feeds.html)
# TODO: MORE INFO: https://astrosat.atlassian.net/browse/SA-154?atlOrigin=eyJpIjoiMDkxMDNmOTU4ZTFlNDNjMzg2Nzk3MzkzMTEyZTk0NWQiLCJwIjoiaiJ9


class AlertGeometry(gis_models.Model):

    PRECISION = 12

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    alert = models.ForeignKey(
        "alert",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name="geometries",
    )

    description = models.TextField(blank=True, null=True)
    geometry = gis_models.GeometryField(blank=False, null=False)
    bounding_box = gis_models.PolygonField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.geometry and self.geometry.geom_type != "Point":
            self.bounding_box = self.geometry.envelope
        return super().save(*args, **kwargs)


class Alert(models.Model):
    class Meta:
        verbose_name = "Alert"
        verbose_name_plural = "Alerts"

    objects = AlertManager.from_queryset(AlertQuerySet)()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    type = models.CharField(
        max_length=128,
        choices=AlertType.choices,
        default=AlertType.UNVALIDATED,
        blank=True,
        null=True,
    )

    timestamp = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=128, blank=True, null=True)
    source = models.CharField(max_length=128, blank=True, null=True)
    scope = models.CharField(max_length=128, blank=True, null=True)

    media = ArrayField(models.URLField(), blank=True, default=list)

    category = models.CharField(max_length=128, blank=True, null=True)
    event = models.CharField(max_length=128, blank=True, null=True)
    urgency = models.CharField(max_length=128, blank=True, null=True)
    severity = models.CharField(max_length=128, blank=True, null=True)
    certainty = models.CharField(max_length=128, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    message = models.JSONField(
        blank=True, null=True, help_text=_("raw message content")
    )

    def validate(self):
        import pdb
        pdb.set_trace()
        pass

    def unvalidate(self):
        import pdb
        pdb.set_trace()
        pass

    @classmethod
    def process_message(cls, message_body, **kwargs):

        message_properties = kwargs.get("properties", {})

        alerts = []

        try:
            with transaction.atomic():
                for info in message_body["info"]:
                    from safers.alerts.serializers import AlertSerializer
                    serializer = AlertSerializer(
                        data={
                            "timestamp":
                                message_body.get("sent"),
                            "status":
                                message_body.get("status"),
                            "source":
                                message_body.get("source"),
                            "scope":
                                message_body.get("scope"),
                            "category":
                                info.get("category"),
                            "event":
                                info.get("event"),
                            "urgency":
                                info.get("urgency"),
                            "severity":
                                info.get("severity"),
                            "certainty":
                                info.get("certainty"),
                            "description":
                                info.get("description"),
                            "geometry":
                                cap_area_to_geojson(info.get("area", []))
                                ["features"],
                            "message":
                                message_body,
                        }
                    )

                    if serializer.is_valid(raise_exception=True):
                        alert = serializer.save()
                        alerts.append(alert)

        except Exception as e:
            msg = f"unable to process_message: {e}"
            raise RMQException(msg)

        return {"detail": [f"created alert: {alert}" for alert in alerts]}


def cap_area_to_geojson(cap_area):
    features = []
    for area in cap_area:

        feature = {
            "type": "Feature",
            "properties": {
                "description": area.get("areaDesc")
            }
        }

        area_keys = {key.title(): key for key in area.keys()}

        if "Polygon" in area_keys:
            feature["geometry"] = {
                "type": "Polygon", "coordinates": area[area_keys["Polygon"]]
            }
        elif "Point" in area_keys:
            lat, lon = list(map(float, area[area_keys["Point"]].split()))
            feature["geometry"] = {
                "type": "Point", "coordinates": geos.Point(lon, lat).coords
            }
        elif "Circle" in area_keys:
            lat, lon, radius = list(map(float, area[area_keys["Circle"]].split()))
            feature["geometry"] = {
                "type": "Polygon",
                "coordinates": geos.Point(lon, lat).buffer(radius).coords
            }
        elif "Geocode" in area_keys:
            raise ValueError("don't know how to cope w/ geocode yet")
        else:
            raise ValueError("unknown area type")

        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features,
    }


###############
# CAP MESSAGE #
###############

{
    "identifier": "identifier",
    "sender": "sem",
    "sent": "2022-04-13T14:28:25+03:00",
    "status": "Actual",
    "msgType": "Alert",
    "source": "Report",
    "scope": "Public",
    "code": [],
    "info": [
        {
            "category": "Fire ",
            "event": "Fire detection in area",
            "urgency": "Immediate",
            "severity": "Severe",
            "certainty": "Likely",
            "description": "description",
            "area": [
                {
                    "areaDesc": "areaDesc",
                    "point" : "40.648142 22.95255"
                }
            ]
        }
    ]
}  # yapf: disable