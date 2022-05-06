from datetime import timedelta
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from safers.core.mixins import SingletonMixin


class SafersSettings(SingletonMixin, models.Model):
    class Meta:
        verbose_name = "Safers Settings"
        verbose_name_plural = "Safers Settings"

    allow_registration = models.BooleanField(
        default=True,
        help_text=_("Allow users to register w/ Safers."),
    )

    require_verification = models.BooleanField(
        default=True,
        help_text=_(
            "Require an email verification step to the sign up process."
        ),
    )

    require_terms_acceptance = models.BooleanField(
        default=True,
        help_text=_(
            "Require a user to accept the terms & conditions during the sign up process."
        ),
    )

    polling_frequency = models.FloatField(
        default=60,
        validators=[MinValueValidator(0)],
        help_text=_(
            "The frequency (in seconds) that the frontend should poll the backend for new data."
        ),
    )

    max_favorite_alerts = models.PositiveBigIntegerField(
        default=3,
        help_text=_("Number of alerts that a user can mark as 'favorite'."),
    )

    max_favorite_events = models.PositiveBigIntegerField(
        default=3,
        help_text=_("Number of alerts that a user can mark as 'favorite'."),
    )

    max_favorite_camera_media = models.PositiveBigIntegerField(
        default=3,
        help_text=_(
            "Number of camera_medias that a user can mark as 'favorite'."
        ),
    )

    default_timerange = models.DurationField(
        default=timedelta(days=3),
        help_text=_(
            "Time range to use in date/datetime filters when no explicit filter is provided."
        )
    )

    possible_event_distance = models.FloatField(
        default=10.0,
        validators=[MinValueValidator(0), MaxValueValidator(1000)],
        help_text=_(
            "Radius (in kms) within which alerts can be transformed into events"
        )
    )

    possible_event_timerange = models.FloatField(
        default=72.0,
        validators=[MinValueValidator(0), MaxValueValidator(168)],
        help_text=_(
            "Time range (in hours) within which alerts can be transformed into events"
        )
    )

    def __str__(self):
        return "Safers Settings"
