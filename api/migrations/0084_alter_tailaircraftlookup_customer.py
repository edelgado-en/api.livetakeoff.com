# Generated by Django 4.1.1 on 2022-11-08 18:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0083_tailaircraftlookup_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tailaircraftlookup',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tail_aircraft_lookup', to='api.customer'),
        ),
    ]