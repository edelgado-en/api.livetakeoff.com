# Generated by Django 4.1.1 on 2024-05-04 10:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0181_remove_userprofile_enable_sms_notification_job_accepted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='enable_sms_notification_job_comment_added',
        ),
    ]
