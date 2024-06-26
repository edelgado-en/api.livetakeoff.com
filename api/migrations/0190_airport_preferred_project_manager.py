# Generated by Django 4.1.1 on 2024-05-14 12:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0189_alter_job_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='airport',
            name='preferred_project_manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='preferred_airports', to=settings.AUTH_USER_MODEL),
        ),
    ]
