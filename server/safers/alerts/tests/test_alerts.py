import pytest
import urllib

from django.urls import resolve, reverse

from rest_framework import status

from safers.core.tests.factories import *
from safers.alerts.tests.factories import *


@pytest.mark.django_db
class TestAlertViews:
    def test_bbox_filter(self, user, api_client):

        alert = AlertFactory()
        (xmin, ymin, xmax, ymax) = alert.geometry.extent

        client = api_client(user)

        in_bounding_box = [xmin, ymin, xmax, ymax]
        out_bounding_box = [
            xmin + (xmax - xmin) + 1,
            ymin + (ymax - ymin) + 1,
            xmax + (xmax - xmin) + 1,
            ymax + (ymax - ymin) + 1,
        ]

        url_params = urllib.parse.urlencode({
            "geometry__bboverlaps": ",".join(map(str, in_bounding_box))
        })
        url = f"{reverse('alerts-list')}?{url_params}"
        response = client.get(url, format="json")
        assert status.is_success(response.status_code)

        content = response.json()
        assert len(content) == 1

        url_params = urllib.parse.urlencode({
            "geometry__bboverlaps": ",".join(map(str, out_bounding_box))
        })
        url = f"{reverse('alerts-list')}?{url_params}"
        response = client.get(url, format="json")
        assert status.is_success(response.status_code)

        content = response.json()
        assert len(content) == 0

    def test_favorite_alert(self, user, api_client, safers_settings):

        safers_settings.max_favorite_alerts = 1
        safers_settings.save()

        alert = AlertFactory()

        client = api_client(user)
        url = reverse("alerts-favorite", args=[alert.id])
        response = client.post(url, format="json")
        assert status.is_success(response.status_code)

        content = response.json()
        assert content["favorite"] == True

        assert alert in user.favorite_alerts.all()

    def test_unfavorite_alert(self, user, api_client, safers_settings):

        safers_settings.max_favorite_alerts = 1
        safers_settings.save()

        alert = AlertFactory()
        user.favorite_alerts.add(alert)

        client = api_client(user)
        url = reverse("alerts-favorite", args=[alert.id])
        response = client.post(url, format="json")
        assert status.is_success(response.status_code)

        content = response.json()
        assert content["favorite"] == False

        assert alert not in user.favorite_alerts.all()

    def test_cannot_favorite_alert(self, user, api_client, safers_settings):

        safers_settings.max_favorite_alerts = 1
        safers_settings.save()

        alerts = [AlertFactory() for _ in range(2)]
        user.favorite_alerts.add(alerts[0])

        client = api_client(user)
        url = reverse("alerts-favorite", args=[alerts[1].id])
        response = client.post(url, format="json")
        assert status.is_client_error(response.status_code)
