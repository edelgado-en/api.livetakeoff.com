# Generated by Django 4.1.1 on 2024-01-11 18:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0146_jobschedule_start_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobschedule',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='jobschedule',
            name='last_job_created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='jobschedule',
            name='repeat_every',
            field=models.PositiveIntegerField(blank=True, help_text='Used for recurrent schedules. It refers to days.', null=True),
        ),
    ]
