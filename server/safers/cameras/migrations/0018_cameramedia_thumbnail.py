# Generated by Django 3.2.18 on 2023-02-28 19:42

from django.db import migrations, models
import safers.cameras.models.models_cameramedia


class Migration(migrations.Migration):

    dependencies = [
        ('cameras', '0017_rename_file_cameramedia_media'),
    ]

    operations = [
        migrations.AddField(
            model_name='cameramedia',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to=safers.cameras.models.models_cameramedia.camera_media_file_path),
        ),
    ]