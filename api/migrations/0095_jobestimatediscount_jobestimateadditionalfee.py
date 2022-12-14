# Generated by Django 4.1.1 on 2022-11-22 15:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0094_jobestimate_airport'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobEstimateDiscount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('type', models.CharField(choices=[('S', 'By Service'), ('A', 'By Airport'), ('G', 'General')], max_length=1)),
                ('percentage', models.BooleanField(default=False)),
                ('job_estimate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_estimate_discounts', to='api.jobestimate')),
            ],
            options={
                'verbose_name_plural': 'Job Estimate Discounts',
            },
        ),
        migrations.CreateModel(
            name='JobEstimateAdditionalFee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=6)),
                ('type', models.CharField(choices=[('F', 'By FBO'), ('A', 'By Airport'), ('G', 'General')], max_length=1)),
                ('percentage', models.BooleanField(default=False)),
                ('job_estimate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_estimate_additional_fees', to='api.jobestimate')),
            ],
            options={
                'verbose_name_plural': 'Job Estimate Additional Fees',
            },
        ),
    ]
