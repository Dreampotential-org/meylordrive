# Generated by Django 4.0.5 on 2022-09-20 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_servergroup'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='servergroup',
            name='servers',
        ),
        migrations.AddField(
            model_name='servergroup',
            name='servers',
            field=models.ManyToManyField(to='tasks.server'),
        ),
    ]
