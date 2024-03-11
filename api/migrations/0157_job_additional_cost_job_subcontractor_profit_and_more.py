# Generated by Django 4.1.1 on 2024-03-09 13:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0156_vendor_is_external'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='additional_cost',
            field=models.DecimalField(decimal_places=2, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='subcontractor_profit',
            field=models.DecimalField(decimal_places=2, help_text='Calculated by subtracting the vendor charge and additional cost from the price', max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='vendor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='api.vendor'),
        ),
        migrations.AddField(
            model_name='job',
            name='vendor_charge',
            field=models.DecimalField(decimal_places=2, max_digits=9, null=True),
        ),
    ]