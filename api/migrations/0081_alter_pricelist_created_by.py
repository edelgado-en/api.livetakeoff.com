# Generated by Django 4.1.1 on 2022-11-06 17:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0080_pricelist_created_at_pricelist_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pricelist',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='pricelists', to=settings.AUTH_USER_MODEL),
        ),
    ]
