# Generated by Django 4.1.1 on 2024-04-11 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0168_customeradditionalfeevendor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customeradditionalfee',
            name='type',
            field=models.CharField(choices=[('F', 'FBO Fee'), ('A', 'Travel Fees'), ('G', 'General'), ('V', 'Higher Vendor Price')], max_length=1),
        ),
    ]
