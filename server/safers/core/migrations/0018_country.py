# Generated by Django 3.2.15 on 2022-08-17 11:53

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20220803_1123'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sovereign_name', models.CharField(max_length=128)),
                ('sovereign_code', models.CharField(max_length=3)),
                ('admin_name', models.CharField(max_length=128)),
                ('admin_code', models.CharField(max_length=3, unique=True)),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(srid=4326)),
            ],
            options={
                'verbose_name': 'Country',
                'verbose_name_plural': 'Countries',
            },
        ),
    ]