# Generated by Django 4.2.2 on 2023-07-06 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0036_alter_datatype_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='datatype',
            name='opacity',
            field=models.FloatField(default=0.5),
        ),
    ]