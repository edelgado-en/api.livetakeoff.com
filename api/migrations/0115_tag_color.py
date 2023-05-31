# Generated by Django 4.1.1 on 2022-12-24 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0114_tag_jobtag'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='color',
            field=models.CharField(choices=[('red', 'red'), ('orange', 'orange'), ('amber', 'amber'), ('yellow', 'yellow'), ('lime', 'lime'), ('green', 'green'), ('indigo', 'indigo'), ('violet', 'violet'), ('purple', 'purple'), ('fuchsia', 'fuchsia'), ('pink', 'pink'), ('rose', 'rose')], default='red', max_length=255),
        ),
    ]