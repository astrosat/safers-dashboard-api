# Generated by Django 3.2.13 on 2022-05-14 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0002_report'),
    ]

    operations = [
        migrations.RenameField(
            model_name='report',
            old_name='external_id',
            new_name='report_id',
        ),
        migrations.RemoveField(
            model_name='report',
            name='_hash',
        ),
        migrations.RemoveField(
            model_name='report',
            name='bounding_box',
        ),
        migrations.RemoveField(
            model_name='report',
            name='data',
        ),
        migrations.AddField(
            model_name='report',
            name='content',
            field=models.CharField(blank=True, choices=[('Submitted', 'Submitted'), ('Inappropriate', 'Inappropriate'), ('Inaccurate', 'Inaccurate'), ('Validated', 'Validated')], max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='hazard',
            field=models.CharField(blank=True, choices=[('Avalanche', 'Avalanche'), ('Earthquake', 'Earthquake'), ('Fire', 'Fire'), ('Flood', 'Flood'), ('Landslide', 'Landslide'), ('Storm', 'Storm'), ('Weather', 'Weather'), ('Subsidence', 'Subsidence')], max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='is_public',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='media',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='report',
            name='mission_id',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='reporter',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='report',
            name='source',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='status',
            field=models.CharField(blank=True, choices=[('Unknown', 'Unknown'), ('Notified', 'Notified'), ('Managed', 'Managed'), ('Closed', 'Closed')], max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='timestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
