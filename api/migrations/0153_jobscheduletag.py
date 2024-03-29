# Generated by Django 4.1.1 on 2024-01-16 13:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0152_jobschedule_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobScheduleTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_schedule', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tags', to='api.jobschedule')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='job_schedule_tags', to='api.tag')),
            ],
        ),
    ]
