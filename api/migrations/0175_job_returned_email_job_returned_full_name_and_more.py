# Generated by Django 4.1.1 on 2024-04-18 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0174_job_accepted_email_job_accepted_full_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='returned_email',
            field=models.CharField(blank=True, max_length=320, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='returned_full_name',
            field=models.CharField(blank=True, help_text='This is the name of the vendor that returned the job via the shareable public link', max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='returned_phone_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
