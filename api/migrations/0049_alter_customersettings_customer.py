# Generated by Django 4.1.1 on 2022-10-05 11:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0048_alter_jobserviceassignment_project_manager'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customersettings',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_settings', to='api.customer'),
        ),
    ]