import json

from django.conf import settings
from django.contrib.gis import geos
from django.db import transaction
from django.utils import timezone

from safers.rmq.exceptions import RMQException

from safers.alerts.models import AlertSource
from safers.alerts.serializers import AlertSerializer

from safers.cameras.models import Camera, CameraMediaType, CameraMediaFireClass, CameraMediaTag
from safers.cameras.serializers import CameraMediaSerializer

FIRE_CLASS_MAP = {
    "not_available": None,
    "class_1": "CL1",
    "class_2": "CL2",
    "class_3": "CL3",
}

TAG_MAP = {
    "not_available": None,
    "fire": "fire",
    "smoke": "smoke",
}


def process_messages(message_body, **kwargs):
    """
    Handler for messages from the cameras service.
    Decides whether to create an Alert instance and/or a CameraMedia instance.
    """

    message_properties = kwargs.get("properties", {})

    details = []

    try:
        with transaction.atomic():

            camera = Camera.objects.get(camera_id=message_body["camera"]["ID"])
            fire_classes = CameraMediaFireClass.objects.filter(
                name__in=[
                    FIRE_CLASS_MAP[k] for k,
                    v in message_body["class_of_fire"].items() if v is True
                ]
            ).values_list("name", flat=True)
            tags = CameraMediaTag.objects.filter(
                name__in=[
                    TAG_MAP[k] for k,
                    v in message_body["detection"].items() if v is True
                ]
            ).values_list("name", flat=True)
            geometry_details = message_body.get("fire_location", {})
            lon, lat = (geometry_details.get("longitude"), geometry_details.get("latitude"))
            geometry = geos.Point(lon, lat) if lon and lat else None

            serializer = CameraMediaSerializer(
                data={
                    "camera_id":
                        camera.camera_id,
                    "type":
                        CameraMediaType.IMAGE,
                    "timestamp":
                        message_body["timestamp"],
                    "remote_url":
                        message_body["link"],
                    "fire_classes":
                        fire_classes,
                    "tags":
                        tags,
                    "distance":
                        geometry_details.get("distance"),
                    "direction":
                        geometry_details.get("direction") or camera.direction,
                    "geometry":
                        geometry or camera.geometry,
                    "message":
                        message_body,
                }
            )

            # create camera_media object...
            # (the post_save signal will take care of camera.last_update)
            if serializer.is_valid(raise_exception=True):
                camera_media = serializer.save()
                camera.refresh_from_db()
                details.append(f"created camera_media: {str(camera_media)}")

            # delete old undetected camera_media objects...
            # (the pre_delete signal will take care of camera.last_update)
            old_undetected_camera_medias = camera.media.undetected().filter(
                timestamp__lt=timezone.now() -
                settings.SAFERS_CAMERA_MEDIA_PRESERVE_TIMERANGE
            ).exclude(pk=camera_media.pk)
            if old_undetected_camera_medias.exists():
                for old_undected_camera_media in old_undetected_camera_medias:
                    details.append(
                        f"deleted old camera_media: {str(old_undected_camera_media)}"
                    )
                    old_undected_camera_media.delete()
                camera.refresh_from_db()

            # maybe create alert
            if camera_media.triggers_alert():
                # yapf: disable
                serializer = AlertSerializer(
                    data={
                        # TODO: CAMERAS NEED CAP INFORMATION
                        "timestamp": camera_media.timestamp,
                        "status": "Actual",
                        "source": AlertSource.IN_SITU,
                        "scope": None,
                        "category": "Fire",
                        "event": None,
                        "urgency": None,
                        "severity": None,
                        "certainty": None,
                        "description": None,
                        "geometry": [{
                            "type": "Feature",
                            "properties": {},
                            "geometry": json.loads(camera.geometry.json)
                        }],
                        # "media": [camera_media.media.url] if camera_media.media else [camera_media.remote_url],
                        # "thumbnails": [camera_media.thumbnail.url] if camera_media.thumbnail else [],
                        "message": message_body,
                    }
                )

                if serializer.is_valid(raise_exception=True):
                    alert = serializer.save()
                    camera_media.alert = alert
                    camera_media.save()
                    details.append(f"created alert: {str(alert)}")

    except Exception as e:
        msg = f"unable to process_message: {e}"
        raise RMQException(msg)

    return {"detail": details}


#######################
# CAMERA MESSAGE BODY #
#######################

{
    "timestamp":
        "2022-01-27T09:48:00.000+0100",
    "camera": {
        "ID": "El_Perello",
        "owner": "PCF",
        "cam_direction": 297,
        "model": "reolink RLC-823A",
        "type": "PTZ",
        "latitude": 40.916961,
        "longitude": 0.694965,
        "altitude": 298
    },
    "detection": {
        "not_available": False, "smoke": False, "fire": False
    },
    "class_of_fire": {
        "not_available": True,
        "class_1": False,
        "class_2": False,
        "class_3": False
    },
    "fire_location": {
        "not_available": False,
        "direction": None,
        "distance": None,
        "latitude": None,
        "longitude": None
    },
    "link":
        "https://s3.eu-central-1.amazonaws.com/waterview.faketp/PCFElPerello_1db3454c2250/2022/05/19/pic_2022-05-19_08-22-40.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAJQR7EL2CSUT7FDIA%2F20220519%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Date=20220519T082248Z&X-Amz-Expires=1200&X-Amz-SignedHeaders=host&X-Amz-Signature=e7e68343d43abaa7bb0771c50bb180e7b7ac0bd11c3aeaf433a8f2c8a90b0a86"
}
