# Generated by Django 4.1.1 on 2022-11-01 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0077_job_on_site'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='completion_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
