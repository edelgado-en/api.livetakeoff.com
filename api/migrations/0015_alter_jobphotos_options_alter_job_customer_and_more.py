# Generated by Django 4.1.1 on 2022-09-29 19:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_remove_jobphotos_photourl_jobphotos_image_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jobphotos',
            options={'verbose_name_plural': 'Job Photos'},
        ),
        migrations.AlterField(
            model_name='job',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='jobs', to='api.customer'),
        ),
        migrations.AlterField(
            model_name='jobcomments',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='api.job'),
        ),
        migrations.AlterField(
            model_name='jobphotos',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='api.job'),
        ),
    ]
