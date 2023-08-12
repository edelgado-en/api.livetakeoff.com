# Generated by Django 4.1.4 on 2023-08-12 09:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_alter_locationitem_minimum_required_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationItemBrand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location_item_brands', to='inventory.brand')),
                ('location_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location_item_brands', to='inventory.locationitem')),
            ],
        ),
    ]
