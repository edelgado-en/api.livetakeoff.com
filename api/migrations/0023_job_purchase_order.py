# Generated by Django 4.1.1 on 2022-10-01 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='purchase_order',
            field=models.CharField(default='', max_length=255),
        ),
    ]