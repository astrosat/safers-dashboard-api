# Generated by Django 3.2.13 on 2022-07-05 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0017_alter_maprequest_request_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='maprequest',
            name='title',
            field=models.CharField(default='title', max_length=255),
            preserve_default=False,
        ),
    ]