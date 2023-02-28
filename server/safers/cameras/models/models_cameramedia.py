import requests
import uuid
from tempfile import TemporaryFile
from urllib.parse import urlparse
from PIL import Image

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q, ExpressionWrapper
from django.contrib.gis.db import models as gis_models
from django.utils.translation import gettext_lazy as _

CAMERA_MEDIA_THUMBNAIL_SIZE = (
    256,
    256,
)

CAMERA_MEDIA_THUMBNAIL_FORMAT = "png"


def camera_media_file_path(instance, filename):
    return f"cameras/{instance.camera}/{filename}"


class CameraMediaType(models.TextChoices):
    IMAGE = "IMAGE", _("Image")
    VIDEO = "VIDEO", _("Video")


class CameraMediaManager(models.Manager):
    pass

    # def get_queryset(self):
    #     queryset = CameraMediaQuerySet(self.model, using=self._db).all()
    #     annotated_queryset = queryset.annotate(
    #         _is_fire=ExpressionWrapper(
    #             Q(tags__name__in=["fire"]), output_field=models.BooleanField()
    #         ),
    #         _is_smoke=ExpressionWrapper(
    #             Q(tags__name__in=["smoke"]), output_field=models.BooleanField()
    #         ),
    #         _is_detected=ExpressionWrapper(
    #             Q(tags__name__in=["fire", "smoke"]),
    #             output_field=models.BooleanField()
    #         ),
    #     )
    #     return annotated_queryset


class CameraMediaQuerySet(models.QuerySet):
    def images(self):
        return self.filter(type=CameraMediaType.IMAGE)

    def videos(self):
        return self.filter(type=CameraMediaType.VIDEO)

    def fire(self):
        return self.filter(tags__name__in=["fire"])
        # return self.filter(_is_fire=True)

    def smoke(self):
        return self.filter(tags__name__in=["smoke"])
        # return self.filter(_is_smoke=True)

    def detected(self):
        return self.filter(tags__name__in=["fire", "smoke"]).distinct()
        # return self.filter(Q(_is_fire=True) | Q(_is_smoke=True))

    def undetected(self):
        return self.exclude(tags__name__in=["fire", "smoke"]).distinct()
        # return self.filter(Q(_is_fire=False) & Q(_is_smoke=False))

    def alerted(self):
        return self.filter(alert__isnull=False)

    def unalerted(self):
        return self.filter(alert__isnull=True)


class CameraMediaFireClass(models.Model):
    class Meta:
        verbose_name = "Fire Class"
        verbose_name_plural = "Fire Classes"

    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class CameraMediaTag(models.Model):
    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class CameraMedia(gis_models.Model):
    class Meta:
        verbose_name = "Camera Media"
        verbose_name_plural = "Camera Media"

    PRECISION = 12

    objects = CameraMediaManager.from_queryset(CameraMediaQuerySet)()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    camera = models.ForeignKey(
        "camera",
        related_name="media",
        blank=False,
        null=False,
        on_delete=models.CASCADE
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    type = models.CharField(
        max_length=64, choices=CameraMediaType.choices, blank=False, null=False
    )

    timestamp = models.DateTimeField(blank=True, null=True)

    description = models.TextField(blank=True, null=True)

    url = models.URLField(
        max_length=512, blank=True, null=True
    )  # pre-signed AWS URLs can be quite long, hence the max_length kwarg

    media = models.FileField(
        blank=True,
        null=True,
        upload_to=camera_media_file_path,
    )

    thumbnail = models.ImageField(
        blank=True,
        null=True,
        upload_to=camera_media_file_path,
    )

    tags = models.ManyToManyField(
        CameraMediaTag,
        blank=True,
        related_name="media",
        help_text=_("Determines whether this media captures fire or smoke")
    )

    fire_classes = models.ManyToManyField(
        CameraMediaFireClass,
        blank=True,
        related_name="media",
        help_text=_(
            "A classification of the type of smoke detected from the camera."
            "Possible classes are: CL1 (fires involving wood/plants), CL2 (fires involving flammable materials/liquids), CL3 (fires involving gas)."
        )
    )

    direction = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(360)],
        help_text=_(
            "The geographical direction in angles of the detected fire with respect to the camera location"
        )
    )
    distance = models.FloatField(
        blank=True,
        null=True,
        help_text=_(
            "The distance in meters of the detected fire with respect to the camera location"
        ),
    )
    geometry = gis_models.GeometryField(blank=True, null=True)

    message = models.JSONField(
        blank=True, null=True, help_text=_("raw message content")
    )

    alert = models.ForeignKey(
        "alerts.alert",
        blank=True,
        null=True,
        related_name="camera_media",
        on_delete=models.SET_NULL,
        help_text=_(
            "The alert that this camera_media might be associated with"
        ),
    )

    @property
    def is_fire(self):
        return self.tags.filter(name__in=["fire"]).exists()

    @property
    def is_smoke(self):
        return self.tags.filter(name__in=["smoke"]).exists()

    @property
    def is_detected(self):
        return self.tags.filter(name__in=["fire", "smoke"]).distinct().exists()

    @property
    def undetected(self):
        return self.tags.exclude(name__in=["fire", "smoke"]).distinct().exists()

    def triggers_alert(self):
        """
        determines whether this camera_media obj warrants the creation of a new alert
        """

        if not self.is_detected:
            return False

        other_camera_medias = self.camera.media.exclude(pk=self.pk)
        other_detected_camera_medias = other_camera_medias.detected()
        other_alerted_detected_camera_medias = other_detected_camera_medias.alerted(
        )
        most_recent_alerted_detected_camera_media = other_alerted_detected_camera_medias.order_by(
            "timestamp"
        ).last()

        return not most_recent_alerted_detected_camera_media or (
            self.timestamp - most_recent_alerted_detected_camera_media.timestamp
        ) >= settings.SAFERS_CAMERA_MEDIA_TRIGGER_ALERT_TIMERANGE

    @staticmethod
    def copy_url_to_media(url, media_field):

        assert url, "URL does not exist"

        file_name = urlparse(url).path.split('/')[-1]
        with TemporaryFile() as temp_file:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            for response_chunk in response.iter_content(chunk_size=4096):
                temp_file.write(response_chunk)
            temp_file.seek(0)
            media_field.save(
                file_name,
                temp_file,
                save=True,
            )

    @staticmethod
    def copy_media_to_thumbnail(media_file, thumbnail_field):

        assert media_file, "media does not exist"

        image = Image.open(media_file)
        image.thumbnail(CAMERA_MEDIA_THUMBNAIL_SIZE, Image.ANTIALIAS)

        file_name = f"thumbnail_{media_file.name.split('/')[-1]}"
        with TemporaryFile() as temp_file:
            image.save(temp_file, format=CAMERA_MEDIA_THUMBNAIL_FORMAT)
            thumbnail_field.save(
                file_name,
                temp_file,
                save=True,
            )

    def save(self, **kwargs):
        retval = super().save(**kwargs)

        if self.url and not self.media:
            CameraMedia.copy_url_to_media(self.url, self.media)

        if self.media and not self.thumbnail:
            CameraMedia.copy_media_to_thumbnail(self.media.file, self.thumbnail)

        return retval
