# Generated by Django 3.2.15 on 2022-09-23 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0024_datatype_group_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='maprequest',
            name='geometry_extent',
            field=models.TextField(
                blank=True,
                help_text='extent of bbox of geometry as a string',
                null=True
            ),
        ),
    ]
