# Generated by Django 3.2.15 on 2022-09-23 09:57

from django.db import migrations


def compute_geometry_extent(apps, schema_editor):

    MapRequestModel = apps.get_model("data", "MapRequest")

    for map_request in MapRequestModel.objects.all():
        if map_request.geometry:
            map_request.geometry_extent = ",".join(
                map(str, map_request.geometry.extent)
            )
            map_request.save()


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0025_maprequest_geometry_extent'),
    ]

    operations = [
        migrations.RunPython(
            compute_geometry_extent, reverse_code=migrations.RunPython.noop
        ),
    ]