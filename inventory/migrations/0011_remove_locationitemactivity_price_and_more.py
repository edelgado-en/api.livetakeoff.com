# Generated by Django 4.1.4 on 2023-08-13 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_alter_locationitemactivity_activity_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='locationitemactivity',
            name='price',
        ),
        migrations.AddField(
            model_name='locationitemactivity',
            name='cost',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Summation of cost per unit and quantity', max_digits=10, null=True),
        ),
    ]
