# Generated by Django 4.2 on 2023-05-28 18:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workers', '0020_alter_workerlogs_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workerlogs',
            name='date',
        ),
        migrations.RemoveField(
            model_name='workerlogs',
            name='time',
        ),
    ]
