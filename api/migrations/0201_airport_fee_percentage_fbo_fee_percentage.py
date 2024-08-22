# Generated by Django 4.1.1 on 2024-08-22 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0200_airport_fee_fbo_fee'),
    ]

    operations = [
        migrations.AddField(
            model_name='airport',
            name='fee_percentage',
            field=models.BooleanField(default=False, help_text='If true, the fee is of type percentage, otherwise it is a fixed fee.'),
        ),
        migrations.AddField(
            model_name='fbo',
            name='fee_percentage',
            field=models.BooleanField(default=False, help_text='If true, the fee is of type percentage, otherwise it is a fixed fee.'),
        ),
    ]
