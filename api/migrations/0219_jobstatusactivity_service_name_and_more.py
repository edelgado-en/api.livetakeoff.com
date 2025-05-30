# Generated by Django 4.1.1 on 2025-05-04 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0218_customerfolloweremail_is_persistent'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobstatusactivity',
            name='service_name',
            field=models.CharField(blank=True, help_text='Name of the service that was added or removed. This includes retainers.', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='jobstatusactivity',
            name='activity_type',
            field=models.CharField(choices=[('E', 'Departure Changed'), ('A', 'Arrival Changed'), ('B', 'Complete Before Changed'), ('P', 'Price Changed'), ('O', 'Airport Changed'), ('F', 'FBO Changed'), ('S', 'Status Changed'), ('T', 'Tail Number Changed'), ('U', 'Photos Uploaded'), ('R', 'Job Returned'), ('V', 'Vendor Accepted'), ('C', 'Service Added'), ('D', 'Service Removed'), ('X', 'Retainer Added'), ('Y', 'Retainer Removed')], default='S', max_length=1),
        ),
    ]
