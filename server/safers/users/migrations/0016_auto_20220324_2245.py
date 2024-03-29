# Generated by Django 3.2.12 on 2022-03-24 22:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
# import safers.users.models.models_profiles


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_user_favorite_camera_medias'),
    ]

    operations = [
        migrations.AddField(
            model_name='oauth2user',
            name='created',
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='oauth2user',
            name='expires_in',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='oauth2user',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='oauth2user',
            name='token_type',
            field=models.CharField(default='Bearer', max_length=64),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="profiles/avatars",
                validators=[]
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='city',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='company',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='country',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='first_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='last_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='oauth2user',
            name='access_token',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='oauth2user',
            name='data',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='oauth2user',
            name='refresh_token',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='oauth2user',
            name='user',
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='auth_user',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name='user',
            name='auth_id',
            field=models.UUIDField(
                blank=True,
                editable=False,
                help_text='The corresponding id of the FusionAuth User',
                null=True,
                unique=True
            ),
        ),
    ]
