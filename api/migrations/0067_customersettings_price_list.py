# Generated by Django 4.1.1 on 2022-10-20 19:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0066_remove_job_assignees'),
    ]

    operations = [
        migrations.AddField(
            model_name='customersettings',
            name='price_list',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer_settings', to='api.pricelist'),
        ),
    ]