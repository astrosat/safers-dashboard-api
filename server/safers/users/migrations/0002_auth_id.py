# Generated by Django 3.2.12 on 2022-03-03 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='auth_id',
            field=models.UUIDField(blank=True, editable=False, help_text='The corresponding id of the FusionAuth User', null=True),
        ),
    ]
