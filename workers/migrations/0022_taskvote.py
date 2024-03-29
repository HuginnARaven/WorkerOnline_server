# Generated by Django 4.2 on 2023-05-30 17:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0006_taskvoting'),
        ('workers', '0021_remove_workerlogs_date_remove_workerlogs_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField()),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.task')),
                ('voting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.taskvoting')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workers.worker')),
            ],
            options={
                'unique_together': {('worker', 'task', 'voting', 'score')},
            },
        ),
    ]
