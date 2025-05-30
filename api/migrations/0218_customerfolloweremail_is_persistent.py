# Generated by Django 4.1.1 on 2025-04-16 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0217_jobfiles_is_customer_only'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerfolloweremail',
            name='is_persistent',
            field=models.BooleanField(default=False, help_text='If true, the email will be automatically added to the follower email list when creating a job.'),
        ),
    ]
