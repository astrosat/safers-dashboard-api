# Generated by Django 3.2.15 on 2022-10-14 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0016_alter_mission_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='mission',
            name='coordinator_person_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mission',
            name='coordinator_team_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
