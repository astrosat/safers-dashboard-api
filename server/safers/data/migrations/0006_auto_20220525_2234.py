# Generated by Django 3.2.13 on 2022-05-25 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0005_auto_20220525_1641'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='datatype',
            name='unique_data_layer_and_category',
        ),
        migrations.RemoveConstraint(
            model_name='datatype',
            name='required_data_layer_and_category',
        ),
        migrations.AddField(
            model_name='datatype',
            name='info',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='datatype',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddConstraint(
            model_name='datatype',
            constraint=models.UniqueConstraint(fields=('datatype_id', 'group', 'subgroup'), name='unique_fields'),
        ),
        migrations.AddConstraint(
            model_name='datatype',
            constraint=models.UniqueConstraint(condition=models.Q(('datatype_id__isnull', True), ('group__isnull', True)), fields=('subgroup',), name='unique_subgroup'),
        ),
        migrations.AddConstraint(
            model_name='datatype',
            constraint=models.UniqueConstraint(condition=models.Q(('datatype_id__isnull', True), ('subgroup__isnull', True)), fields=('group',), name='unique_group'),
        ),
        migrations.AddConstraint(
            model_name='datatype',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('datatype_id__isnull', False), ('group__isnull', False), ('subgroup__isnull', False)), models.Q(('datatype_id__isnull', True), ('group__isnull', False), ('subgroup__isnull', True)), models.Q(('datatype_id__isnull', True), ('group__isnull', True), ('subgroup__isnull', False)), _connector='OR'), name='non_null_fields'),
        ),
    ]
