# Generated by Django 3.2.12 on 2022-03-29 22:25

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('chatbot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('_hash', models.UUIDField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('external_id', models.CharField(max_length=128, unique=True)),
                ('data', models.JSONField(default=dict)),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(srid=4326)),
                ('bounding_box', django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326)),
            ],
            options={
                'verbose_name': 'Report',
                'verbose_name_plural': 'Reports',
            },
        ),
    ]
