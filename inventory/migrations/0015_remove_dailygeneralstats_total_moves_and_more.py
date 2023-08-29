# Generated by Django 4.1.1 on 2023-08-28 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0014_dailygeneralstats_dailylocationstats'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dailygeneralstats',
            name='total_moves',
        ),
        migrations.RemoveField(
            model_name='dailylocationstats',
            name='total_moves',
        ),
        migrations.AddField(
            model_name='dailygeneralstats',
            name='total_moving_cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='dailygeneralstats',
            name='total_moving_items',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dailygeneralstats',
            name='total_moving_quantity',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dailylocationstats',
            name='total_moving_cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='dailylocationstats',
            name='total_moving_items',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dailylocationstats',
            name='total_moving_quantity',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
