# Generated by Django 4.1.1 on 2022-11-22 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0098_servicetype_service_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicetype',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
