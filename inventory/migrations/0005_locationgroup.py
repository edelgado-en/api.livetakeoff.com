# Generated by Django 4.1.4 on 2023-08-11 12:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_group_remove_item_brand_locationitem_brand_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location_groups', to='inventory.group')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location_groups', to='inventory.location')),
            ],
        ),
    ]
