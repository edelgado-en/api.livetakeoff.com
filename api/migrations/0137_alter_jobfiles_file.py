# Generated by Django 4.1.1 on 2023-11-16 14:30

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0136_jobfiles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobfiles',
            name='file',
            field=cloudinary.models.CloudinaryField(max_length=255, verbose_name='file'),
        ),
    ]
