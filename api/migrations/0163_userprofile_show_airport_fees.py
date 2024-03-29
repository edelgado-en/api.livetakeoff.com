# Generated by Django 4.1.1 on 2024-03-29 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0162_userprofile_show_all_services_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='show_airport_fees',
            field=models.BooleanField(default=False, help_text='If enabled, the user will be able to see airport and fbo additional fees when creating a job. The information will be shown when selecting an airport or fbo.'),
        ),
    ]
