# Generated by Django 4.1.1 on 2023-12-26 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0143_job_hours_worked_job_minutes_worked_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='labor_time',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
