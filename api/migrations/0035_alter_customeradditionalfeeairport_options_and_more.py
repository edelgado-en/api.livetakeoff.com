# Generated by Django 4.1.1 on 2022-10-02 15:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0034_alter_customeradditionalfeefbo_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customeradditionalfeeairport',
            options={'verbose_name_plural': 'Customer Additional Fee Airports'},
        ),
        migrations.CreateModel(
            name='CustomerRetainerService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_setting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='retainer_services', to='api.customersettings')),
                ('retainer_service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.retainerservice')),
            ],
        ),
    ]
