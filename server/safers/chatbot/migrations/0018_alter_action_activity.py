# Generated by Django 3.2.16 on 2023-01-31 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0017_auto_20221014_1023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='activity',
            field=models.CharField(blank=True, choices=[('Surveillance', 'Surveillance'), ('In activity in operative centers', 'In activity in operative centers'), ('Logistics', 'Logistics'), ('AIB Modules', 'AIB Modules'), ('Mobile tubs AIB', 'Mobile tubs AIB'), ('Powered equip.', 'Powered equip.'), ('Manual equip.', 'Manual equip.'), ('Pumping equip.', 'Pumping equip.'), ('Barriers', 'Barriers'), ('Operative machines', 'Operative machines'), ('Assistance to the population', 'Assistance to the population'), ('Fire ext. system', 'Fire ext. system'), ('Fuel reduction', 'Fuel reduction'), ('Fire suppression', 'Fire suppression'), ('Impact assessment', 'Impact assessment'), ('Repair', 'Repair'), ('Evacuation', 'Evacuation'), ('Search and rescue', 'Search and rescue'), ('Rubble removal', 'Rubble removal'), ('Search missing', 'Search missing'), ('Patrolling', 'Patrolling'), ('Check report', 'Check report'), ('Fire extinguishing', 'Fire extinguishing'), ('Remediation', 'Remediation'), ('Restoration', 'Restoration'), ('Mobile tubs', 'Mobile tubs'), ('Line assembly', 'Line assembly'), ('Fire patrolling', 'Fire patrolling'), ('Check fire report', 'Check fire report')], max_length=128, null=True),
        ),
    ]