# Generated by Django 4.1.1 on 2023-03-30 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0123_alter_tag_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pricelistentries',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True),
        ),
    ]
