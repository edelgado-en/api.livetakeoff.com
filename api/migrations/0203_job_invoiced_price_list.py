# Generated by Django 4.1.1 on 2024-09-10 11:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0202_remove_userprofile_show_all_services_report_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='invoiced_price_list',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='api.pricelist'),
        ),
    ]
