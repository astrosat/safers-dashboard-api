# Generated by Django 3.2.14 on 2022-07-07 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0018_maprequest_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maprequest',
            name='request_id',
            field=models.CharField(max_length=255),
        ),
    ]