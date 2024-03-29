# Generated by Django 3.2.12 on 2022-03-28 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aois', '0004_alter_aoi_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aoi',
            name='name',
            field=models.CharField(max_length=128),
        ),
        migrations.AddConstraint(
            model_name='aoi',
            constraint=models.UniqueConstraint(fields=('country', 'name'), name='unique_country_name'),
        ),
    ]
