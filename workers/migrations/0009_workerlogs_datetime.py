# Generated by Django 4.0.1 on 2023-05-07 12:52

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('workers', '0008_alter_worker_day_end_alter_worker_day_start'),
    ]

    operations = [
        migrations.AddField(
            model_name='workerlogs',
            name='datetime',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]