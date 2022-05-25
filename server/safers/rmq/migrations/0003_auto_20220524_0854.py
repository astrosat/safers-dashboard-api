# Generated by Django 3.2.13 on 2022-05-24 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rmq', '0002_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_demo',
            field=models.BooleanField(default=False, help_text='Identifies messages that should be used for demos, etc.'),
        ),
        migrations.AddField(
            model_name='message',
            name='name',
            field=models.CharField(blank=True, help_text='Provides a way to identify messages in order to re-use them for demos, etc.', max_length=128, null=True),
        ),
    ]