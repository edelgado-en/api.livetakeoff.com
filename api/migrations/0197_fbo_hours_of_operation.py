# Generated by Django 4.1.1 on 2024-07-22 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0196_help_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='fbo',
            name='hours_of_operation',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
