# Generated by Django 3.2.12 on 2022-03-09 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auth_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='accepted_terms',
            field=models.BooleanField(default=False, help_text='Has this user accepted the terms & conditions?'),
        ),
    ]
