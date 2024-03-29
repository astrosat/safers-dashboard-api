# Generated by Django 3.2.14 on 2022-08-03 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_siteprofile_data'),
    ]

    operations = [
        migrations.RenameField(
            model_name='saferssettings',
            old_name='allow_registration',
            new_name='allow_signup',
        ),
        migrations.AddField(
            model_name='saferssettings',
            name='allow_local_signin',
            field=models.BooleanField(default=False, help_text='Allow users to signin locally.'),
        ),
        migrations.AddField(
            model_name='saferssettings',
            name='allow_remote_signin',
            field=models.BooleanField(default=True, help_text='Allow users to signin remotely (via SSO).'),
        ),
    ]
