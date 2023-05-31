# Generated by Django 4.1.1 on 2022-12-26 00:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0116_alter_tag_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(choices=[('red', 'red'), ('orange', 'orange'), ('amber', 'amber'), ('indigo', 'indigo'), ('violet', 'violet'), ('fuchsia', 'fuchsia'), ('pink', 'pink')], default='red', max_length=255),
        ),
    ]