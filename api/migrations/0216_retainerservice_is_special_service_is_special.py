# Generated by Django 4.1.1 on 2025-02-18 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0215_tailident'),
    ]

    operations = [
        migrations.AddField(
            model_name='retainerservice',
            name='is_special',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='service',
            name='is_special',
            field=models.BooleanField(default=False),
        ),
    ]
