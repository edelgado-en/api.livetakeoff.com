# Generated by Django 4.1.1 on 2022-10-28 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0075_alter_customer_emailaddress_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='is_auto_priced',
            field=models.BooleanField(default=True),
        ),
    ]
