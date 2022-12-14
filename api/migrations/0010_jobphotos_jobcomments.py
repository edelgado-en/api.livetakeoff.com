# Generated by Django 4.1.1 on 2022-09-27 21:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0009_job'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobPhotos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photourl', models.URLField()),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.job')),
            ],
        ),
        migrations.CreateModel(
            name='JobComments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('date', models.DateTimeField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.job')),
            ],
        ),
    ]
