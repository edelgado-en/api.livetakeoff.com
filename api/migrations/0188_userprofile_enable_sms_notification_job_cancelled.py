# Generated by Django 4.1.1 on 2024-05-04 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0187_userprofile_enable_sms_notification_job_started'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='enable_sms_notification_job_cancelled',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an sms notification when a job is cancelled.'),
        ),
    ]
