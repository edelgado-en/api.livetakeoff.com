# Generated by Django 4.1.1 on 2022-11-25 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0101_airport_public_fbo_public'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='sms_notifications',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='email_notifications',
            field=models.BooleanField(default=False),
        ),
    ]
