# Generated by Django 3.2.13 on 2022-05-24 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rmq', '0003_auto_20220524_0854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='body',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='message',
            name='routing_key',
            field=models.CharField(default=str, max_length=255),
        ),
    ]