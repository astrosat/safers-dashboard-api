# Generated by Django 3.2.13 on 2022-05-13 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0006_auto_20220511_1259'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='type',
            field=models.CharField(blank=True, choices=[('RECOMMENDATION', 'Recommendation (from CERTH)'), ('SYSTEM NOTIFICATION', 'System Update')], max_length=128, null=True),
        ),
    ]
