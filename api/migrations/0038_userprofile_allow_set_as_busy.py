# Generated by Django 4.1.1 on 2022-10-03 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0037_pricelist_pricelistentries'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='allow_set_as_busy',
            field=models.BooleanField(default=False),
        ),
    ]
