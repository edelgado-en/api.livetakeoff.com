# Generated by Django 4.1.1 on 2022-10-02 11:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0030_alter_customerdiscount_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customerdiscountservice',
            options={'verbose_name_plural': 'Customer Discount Service'},
        ),
        migrations.CreateModel(
            name='CustomerDiscountAirport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('airport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.airport')),
                ('customer_discount', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='airports', to='api.customerdiscount')),
            ],
            options={
                'verbose_name_plural': 'Customer Discount Airport',
            },
        ),
    ]