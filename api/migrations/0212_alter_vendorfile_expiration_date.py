# Generated by Django 4.1.1 on 2024-12-27 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0211_vendorfile_expiration_date_vendorfile_file_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendorfile',
            name='expiration_date',
            field=models.DateTimeField(blank=True, help_text='Applicable for insurance files', null=True),
        ),
    ]