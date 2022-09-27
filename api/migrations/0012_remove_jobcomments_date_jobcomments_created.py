# Generated by Django 4.1.1 on 2022-09-27 21:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_customer_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobcomments',
            name='date',
        ),
        migrations.AddField(
            model_name='jobcomments',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]