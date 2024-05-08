# Generated by Django 4.1.1 on 2024-05-03 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0179_userprofile_enable_all_airports_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='enable_email_notification_inventory_out_of_stock',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an email notification when an inventory item is out of stock.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='enable_email_notification_inventory_threshold_met',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an email notification when an inventory item reaches its threshold.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='enable_email_notification_job_accepted',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an email notification when a job is accepted.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='enable_email_notification_job_assigned',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an email notification when a job is assigned.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='enable_email_notification_job_comment_added',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an email notification when a comment is added to a job.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='enable_email_notification_job_completed',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an email notification when a job is completed.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='enable_email_notification_job_confirmed',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an email notification when a job is confirmed.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='enable_email_notification_job_created',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an email notification when a job is created.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='enable_email_notification_job_returned',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an email notification when a job is returned.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='enable_email_notification_scheduled_job_created',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an email notification when a scheduled job is created.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='enable_sms_notification_inventory_out_of_stock',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an sms notification when an inventory item is out of stock.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='enable_sms_notification_inventory_threshold_met',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an sms notification when an inventory item reaches its threshold.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='enable_sms_notification_job_accepted',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an sms notification when a job is accepted.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='enable_sms_notification_job_assigned',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an sms notification when a job is assigned.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='enable_sms_notification_job_comment_added',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an sms notification when a comment is added to a job.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='enable_sms_notification_job_completed',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an sms notification when a job is completed.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='enable_sms_notification_job_confirmed',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an sms notification when a job is confirmed.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='enable_sms_notification_job_created',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an sms notification when a job is created.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='enable_sms_notification_job_returned',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an sms notification when a job is returned.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='enable_sms_notification_scheduled_job_created',
            field=models.BooleanField(default=False, help_text='If enabled, the user will receive an sms notification when a scheduled job is created.'),
        ),
    ]
