# Generated by Django 3.2.15 on 2022-09-01 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0013_auto_20220829_1841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mission',
            name='status',
            field=models.CharField(choices=[('Created', 'Created'), ('TakenInCharge', 'Taken In Charge'), ('Completed', 'Completed'), ('Deleted', 'Deleted')], default='Created', max_length=64),
        ),
    ]