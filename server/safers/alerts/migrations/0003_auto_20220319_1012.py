# Generated by Django 3.2.12 on 2022-03-19 10:12

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0002_alert'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='_hash',
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='alert',
            name='bounding_box',
            field=django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326),
        ),
        migrations.AddField(
            model_name='alert',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='alert',
            name='media',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.URLField(), blank=True, default=list, size=None),
        ),
        migrations.AddField(
            model_name='alert',
            name='source',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='alert',
            name='status',
            field=models.CharField(blank=True, choices=[('UNVALIDATED', 'Unvalidated'), ('VALIDATED', 'Validated'), ('POSSIBLE_EVENT', 'Possible Event')], default='UNVALIDATED', max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='alert',
            name='timestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
