# Generated by Django 4.2 on 2023-05-22 11:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_remove_userprofile_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]