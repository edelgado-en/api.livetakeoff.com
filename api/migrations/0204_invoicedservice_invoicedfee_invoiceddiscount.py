# Generated by Django 4.1.1 on 2024-09-10 15:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0203_job_invoiced_price_list'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvoicedService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=9)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoiced_services', to='api.job')),
            ],
        ),
        migrations.CreateModel(
            name='InvoicedFee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fee', models.DecimalField(decimal_places=2, max_digits=9)),
                ('fee_dollar_amount', models.DecimalField(decimal_places=2, max_digits=9)),
                ('type', models.CharField(choices=[('F', 'FBO Fee'), ('A', 'Travel Fees'), ('G', 'General'), ('V', 'Higher Vendor Price'), ('M', 'Management Fees')], max_length=1)),
                ('percentage', models.BooleanField(default=False)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoiced_fees', to='api.job')),
            ],
        ),
        migrations.CreateModel(
            name='InvoicedDiscount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount', models.IntegerField()),
                ('discount_dollar_amount', models.DecimalField(decimal_places=2, max_digits=9)),
                ('type', models.CharField(choices=[('S', 'By Service'), ('A', 'By Airport'), ('G', 'General')], max_length=1)),
                ('percentage', models.BooleanField(default=False)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoiced_discounts', to='api.job')),
            ],
        ),
    ]
