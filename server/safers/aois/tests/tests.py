""" Test AOIs. """
import pytest
import json

from factory.faker import Faker as FactoryFaker
from itertools import chain

from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APIClient
from rest_framework.utils.encoders import JSONEncoder

from django.contrib.gis.geos import GEOSGeometry, Point, Polygon
from django.urls import reverse

from safers.core.tests.providers import GeometryProvider

from safers.aois.models import Aoi
from safers.aois.serializers import AoiSerializer

from .factories import *

FactoryFaker.add_provider(GeometryProvider)


@pytest.mark.django_db
class TestAoiSerializer:
    def test_serializes_to_featurecollection(self):
        """
        checks that a single AOI serializes to a FeatureCollection w/ one Feature
        """

        aoi = AoiFactory()
        serializer = AoiSerializer(instance=aoi)
        aoi_data = json.loads(json.dumps(serializer.data, cls=JSONEncoder))

        assert aoi_data["type"] == "FeatureCollection"
        assert len(aoi_data["features"]) == 1

        feature = aoi_data["features"][0]
        feature_geometry = feature["geometry"]
        feature_properties = feature["properties"]

        assert feature["type"] == "Feature"

        flattened_model_geometry = list(
            chain.from_iterable(*aoi.geometry.coords)
        )
        flattened_serialized_geometry = list(
            chain.from_iterable(*feature_geometry["coordinates"])
        )
        assert flattened_model_geometry == flattened_serialized_geometry

        assert feature_properties["id"] == aoi.id
        assert feature_properties["name"] == aoi.name
        assert feature_properties["description"] == aoi.description
        assert feature_properties["country"] == aoi.country
        assert feature_properties["zoom_level"] == aoi.zoom_level
        assert feature_properties["midpoint"] == list(aoi.midpoint.coords)

    def test_serializes_from_featurecollection(self):
        """
        checks that a FeatureCollection w/ one Feature can be marshalled into single AOI
        """

        test_aoi = AoiFactory.build(geometry=FactoryFaker("multipolygon"))
        test_serializer = AoiSerializer(instance=test_aoi)
        test_aoi_data = json.loads(
            json.dumps(test_serializer.data, cls=JSONEncoder)
        )
        serializer = AoiSerializer(data=test_aoi_data)
        assert serializer.is_valid()
        aoi = serializer.save()

        assert Aoi.objects.count() == 1

        assert aoi.pk is not None
        assert aoi.name == test_aoi.name
        assert aoi.midpoint == test_aoi.midpoint
        assert aoi.geometry == test_aoi.geometry