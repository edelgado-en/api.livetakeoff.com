# Generated by Django 4.1.1 on 2022-11-17 00:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0088_tailretainerservicelookup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tailaircraftlookup',
            name='tail_number',
            field=models.CharField(max_length=255),
        ),
    ]
