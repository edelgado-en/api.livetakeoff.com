# Generated by Django 4.1.1 on 2024-01-13 14:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0150_jobschedule_is_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='job_schedule',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='api.jobschedule'),
        ),
    ]
