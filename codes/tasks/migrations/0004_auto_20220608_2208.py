# Generated by Django 2.2.20 on 2022-06-08 22:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_auto_tasks_stdout_stderr'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pipeline',
            name='task',
        ),
        migrations.DeleteModel(
            name='Task',
        ),
    ]
