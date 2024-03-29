# Generated by Django 3.2.13 on 2022-05-17 11:15

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0006_rename_type_socialevent_severity'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tweet',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False
                    )
                ),
                ('tweet_id', models.CharField(max_length=128, unique=True)),
                ('timestamp', models.DateTimeField(blank=True, null=True)),
                ('text', models.TextField(blank=True, null=True)),
                (
                    # a previous migration used social.tweet.geometry
                    # so I use the name social.tweet.tmp_geometry
                    # and rename it in migration 0008
                    'tmp_geometry',
                    django.contrib.gis.db.models.fields.GeometryField(
                        srid=4326
                    )
                ),
            ],
            options={
                'verbose_name': 'Tweet',
                'verbose_name_plural': 'Tweets',
            },
        ),
    ]
