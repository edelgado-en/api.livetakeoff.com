# Generated by Django 4.1.1 on 2024-05-16 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0190_airport_preferred_project_manager'),
    ]

    operations = [
        migrations.AddField(
            model_name='customersettings',
            name='enable_approval_process',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customersettings',
            name='enable_auto_assignment',
            field=models.BooleanField(default=False),
        ),
    ]
