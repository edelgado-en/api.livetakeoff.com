# Generated by Django 4.1.1 on 2024-04-18 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0173_userprofile_enable_accept_jobs'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='accepted_email',
            field=models.CharField(blank=True, max_length=320, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='accepted_full_name',
            field=models.CharField(blank=True, help_text='This is the name of the vendor that accepted the job via the shareable public link', max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='accepted_phone_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='jobstatusactivity',
            name='activity_type',
            field=models.CharField(choices=[('E', 'Departure Changed'), ('A', 'Arrival Changed'), ('B', 'Complete Before Changed'), ('P', 'Price Changed'), ('O', 'Airport Changed'), ('F', 'FBO Changed'), ('S', 'Status Changed'), ('T', 'Tail Number Changed'), ('U', 'Photos Uploaded'), ('R', 'Job Returned'), ('V', 'Vendor Accepted')], default='S', max_length=1),
        ),
    ]
