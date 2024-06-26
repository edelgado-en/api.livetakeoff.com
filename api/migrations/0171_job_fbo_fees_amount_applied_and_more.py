# Generated by Django 4.1.1 on 2024-04-12 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0170_alter_customeradditionalfee_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='fbo_fees_amount_applied',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9),
        ),
        migrations.AddField(
            model_name='job',
            name='management_fees_amount_applied',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9),
        ),
        migrations.AddField(
            model_name='job',
            name='travel_fees_amount_applied',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9),
        ),
        migrations.AddField(
            model_name='job',
            name='vendor_higher_price_amount_applied',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9),
        ),
    ]
