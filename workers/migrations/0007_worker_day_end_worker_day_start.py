# Generated by Django 4.0.1 on 2023-04-29 17:29

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('workers', '0006_remove_worker_day_end_remove_worker_day_start_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='worker',
            name='day_end',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='worker',
            name='day_start',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
