# Generated by Django 3.2.15 on 2022-08-16 15:54

from django.db import migrations, models
import safers.chatbot.models.models_reports


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0006_mission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='hazard',
            field=models.CharField(
                blank=True,
                choices=[('Avalanche', 'Avalanche'),
                         ('Earthquake', 'Earthquake'), ('Fire', 'Fire'),
                         ('Flood', 'Flood'), ('Landslide', 'Landslide'),
                         ('Storm', 'Storm'), ('Weather', 'Weather'),
                         ('Subsidence', 'Subsidence')],
                default='Fire',
                max_length=128,
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='report',
            name='media',
            field=models.JSONField(
                default=list,
                validators=[
                    safers.chatbot.models.models_reports.validate_media
                ]
            ),
        ),
        migrations.AlterField(
            model_name='report',
            name='reporter',
            field=models.JSONField(
                default=dict,
                validators=[
                    safers.chatbot.models.models_reports.validate_reporter
                ]
            ),
        ),
        migrations.AlterField(
            model_name='report',
            name='source',
            field=models.CharField(
                blank=True,
                choices=[('Chatbot', 'Chatbot')],
                default='Chatbot',
                max_length=64,
                null=True
            ),
        ),
    ]
