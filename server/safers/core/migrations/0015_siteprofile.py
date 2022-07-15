# Generated by Django 3.2.13 on 2022-07-01 12:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('core', '0014_saferssettings_request_timeout'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=8, null=True, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('site', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='sites.site')),
            ],
            options={
                'verbose_name': 'Site Profile',
                'verbose_name_plural': 'Site Profiles',
            },
        ),
    ]