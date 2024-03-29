# Generated by Django 3.2.12 on 2022-03-30 17:50

from django.db import migrations


def update_profiles_for_existing_users(apps, schema_editor):

    UserModel = apps.get_model("users", "User")
    UserProfileModel = apps.get_model("users", "UserProfile")

    for user in UserModel.objects.all():
        user_profile, _ = UserProfileModel.objects.get_or_create(user=user)

        changed_first_name = changed_last_name = False

        first_name = user.first_name
        if first_name and first_name != user_profile.first_name:
            user_profile.first_name = first_name
            changed_first_name = True

        last_name = user.last_name
        if last_name and last_name != user_profile.last_name:
            user_profile.last_name = last_name
            changed_last_name = True

        if changed_first_name or changed_last_name:
            user_profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_auto_20220330_1250'),
    ]

    operations = [
        migrations.RunPython(
            update_profiles_for_existing_users,
            reverse_code=migrations.RunPython.noop
        ),
    ]