# Generated by Django 3.2.12 on 2022-04-26 14:55

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=128, null=True)),
                ('source', models.CharField(blank=True, max_length=128, null=True)),
                ('scope', models.CharField(blank=True, max_length=128, null=True)),
                ('category', models.CharField(blank=True, max_length=128, null=True)),
                ('event', models.CharField(blank=True, max_length=128, null=True)),
                ('urgency', models.CharField(blank=True, max_length=128, null=True)),
                ('severity', models.CharField(blank=True, max_length=128, null=True)),
                ('certainty', models.CharField(blank=True, max_length=128, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('message', models.JSONField(blank=True, help_text='raw message content', null=True)),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notification',
            },
        ),
    ]