# Generated by Django 4.0.1 on 2023-04-22 21:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='worker',
            name='day_end',
            field=models.TimeField(default=datetime.time(18, 0)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='worker',
            name='day_start',
            field=models.TimeField(default=datetime.time(8, 0)),
            preserve_default=False,
        ),
    ]
