# Generated by Django 4.1.1 on 2023-11-29 12:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0141_tailfile'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCustomer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_customers', to='api.customer')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_customers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'customer')},
            },
        ),
    ]