# Generated by Django 4.1.1 on 2023-03-04 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0121_jobestimate_show_totals'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='short_name',
            field=models.CharField(blank=True, help_text='Short name for use in the UI (e.g. "LA" for "Late Arrival")', max_length=255, null=True),
        ),
    ]