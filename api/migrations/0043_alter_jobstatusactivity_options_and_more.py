# Generated by Django 4.1.1 on 2022-10-03 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0042_alter_estimatedservicetime_estimated_time_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jobstatusactivity',
            options={'verbose_name_plural': 'Job Status Activities'},
        ),
        migrations.AlterField(
            model_name='service',
            name='checklistActions',
            field=models.ManyToManyField(blank=True, related_name='checklistActions', to='api.checklistaction'),
        ),
    ]
