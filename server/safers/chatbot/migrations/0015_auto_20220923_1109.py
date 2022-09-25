# Generated by Django 3.2.15 on 2022-09-23 11:09

from django.db import migrations, models
import safers.chatbot.models.models_communications


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0014_alter_mission_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='communication',
            name='assigned_to',
        ),
        migrations.RemoveField(
            model_name='communication',
            name='target_organizations',
        ),
        migrations.AddField(
            model_name='communication',
            name='target_organizations',
            field=models.JSONField(default=list, validators=[safers.chatbot.models.models_communications.validate_target_organizations]),
        ),
    ]