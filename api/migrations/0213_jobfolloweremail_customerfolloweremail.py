# Generated by Django 4.1.1 on 2025-01-07 12:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0212_alter_vendorfile_expiration_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobFollowerEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=255)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follower_emails', to='api.job')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerFollowerEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=255)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follower_emails', to='api.customer')),
            ],
        ),
    ]
