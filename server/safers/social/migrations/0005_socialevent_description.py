# Generated by Django 3.2.12 on 2022-03-29 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0004_auto_20220329_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialevent',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
