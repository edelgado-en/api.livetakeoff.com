# Generated by Django 4.1.1 on 2024-08-14 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0198_jobestimate_accepted_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='airport',
            name='airport_type',
            field=models.CharField(choices=[('E', 'External'), ('I', 'Internal'), ('B', 'Both')], default='E', max_length=1),
        ),
    ]