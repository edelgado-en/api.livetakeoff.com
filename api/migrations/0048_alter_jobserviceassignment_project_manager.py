# Generated by Django 4.1.1 on 2022-10-05 11:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0047_job_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobserviceassignment',
            name='project_manager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='job_service_assignments', to=settings.AUTH_USER_MODEL),
        ),
    ]