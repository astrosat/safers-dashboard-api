# Generated by Django 4.2 on 2023-05-22 14:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0029_alter_organization_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='role',
            options={'managed': False},
        ),
    ]
