# Generated by Django 4.0.1 on 2023-05-07 19:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0004_company_timezone'),
        ('workers', '0010_workertaskcomment'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='WorkersTasks',
            new_name='TaskAppointment',
        ),
    ]