# Generated by Django 4.1.1 on 2022-10-20 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0069_customeradditionalfee_percentage_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='logo',
            field=models.ImageField(blank=True, upload_to='customers/'),
        ),
    ]