# Generated by Django 4.1.1 on 2024-05-04 12:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0183_remove_userprofile_enable_email_notification_job_assigned_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='enable_sms_notification_job_confirmed',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='enable_sms_notification_job_returned',
        ),
    ]
