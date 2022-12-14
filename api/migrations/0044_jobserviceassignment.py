# Generated by Django 4.1.1 on 2022-10-04 19:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0043_alter_jobstatusactivity_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobServiceAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('A', 'Assigned'), ('W', 'WIP'), ('C', 'Completed')], default='A', max_length=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='job_service_assignments', to='api.job')),
                ('project_manager', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.service')),
            ],
            options={
                'db_table': 'Job Service Assignments',
            },
        ),
    ]
