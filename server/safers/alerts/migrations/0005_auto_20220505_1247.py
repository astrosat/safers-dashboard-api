# Generated by Django 3.2.12 on 2022-05-05 12:47

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0004_auto_20220502_0940'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='alertgeometry',
            options={'verbose_name': 'Alert Geometry', 'verbose_name_plural': 'Alert Geometries'},
        ),
        migrations.AddField(
            model_name='alert',
            name='bounding_box',
            field=django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326),
        ),
        migrations.AddField(
            model_name='alert',
            name='center',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
        migrations.AddField(
            model_name='alertgeometry',
            name='_hash',
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='alertgeometry',
            name='center',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
    ]
