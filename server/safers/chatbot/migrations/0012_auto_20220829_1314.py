# Generated by Django 3.2.15 on 2022-08-29 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0011_mission_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mission',
            name='end_inclusive',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='mission',
            name='start_inclusive',
            field=models.BooleanField(default=True),
        ),
    ]