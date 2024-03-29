# Generated by Django 4.2 on 2023-05-22 23:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workers', '0013_alter_taskappointment_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkerSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monday', models.BooleanField(default=False)),
                ('tuesday', models.BooleanField(default=False)),
                ('wednesday', models.BooleanField(default=False)),
                ('thursday', models.BooleanField(default=False)),
                ('friday', models.BooleanField(default=False)),
                ('saturday', models.BooleanField(default=False)),
                ('sunday', models.BooleanField(default=False)),
                ('worker', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='workers.worker', verbose_name='schedule')),
            ],
        ),
    ]
