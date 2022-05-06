# Generated by Django 3.2.12 on 2022-05-05 15:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_saferssettings_max_favorite_camera_media'),
    ]

    operations = [
        migrations.AddField(
            model_name='saferssettings',
            name='default_timerange',
            field=models.DurationField(default=datetime.timedelta(days=3), help_text='Time range to use in date/datetime filters when no explicit filter is provided.'),
        ),
    ]