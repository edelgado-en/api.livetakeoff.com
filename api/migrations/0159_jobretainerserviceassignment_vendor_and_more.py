# Generated by Django 4.1.1 on 2024-03-10 13:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0158_rename_additional_cost_job_interval_additional_cost_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobretainerserviceassignment',
            name='vendor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='api.vendor'),
        ),
        migrations.AddField(
            model_name='jobserviceassignment',
            name='vendor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='api.vendor'),
        ),
    ]