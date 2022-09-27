# Generated by Django 4.1.1 on 2022-09-27 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_retainerservice'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChecklistAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='service',
            name='checklistActions',
            field=models.ManyToManyField(related_name='checklistActions', to='api.checklistaction'),
        ),
    ]
