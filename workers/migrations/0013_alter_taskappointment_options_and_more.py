# Generated by Django 4.2 on 2023-05-22 14:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workers', '0012_alter_workertaskcomment_task_appointment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='taskappointment',
            options={'verbose_name': 'task appointment', 'verbose_name_plural': 'tasks appointments'},
        ),
        migrations.AlterModelOptions(
            name='workerlogs',
            options={'verbose_name': 'worker`s log', 'verbose_name_plural': 'worker`s logs'},
        ),
        migrations.AlterModelOptions(
            name='workertaskcomment',
            options={'verbose_name': 'task comment', 'verbose_name_plural': 'tasks comments'},
        ),
    ]
