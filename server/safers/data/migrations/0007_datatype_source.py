# Generated by Django 3.2.13 on 2022-06-27 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0006_auto_20220525_2234'),
    ]

    operations = [
        migrations.AddField(
            model_name='datatype',
            name='source',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]