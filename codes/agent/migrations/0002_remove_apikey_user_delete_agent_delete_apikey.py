# Generated by Django 4.0.5 on 2023-11-13 20:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='apikey',
            name='user',
        ),
        migrations.DeleteModel(
            name='Agent',
        ),
        migrations.DeleteModel(
            name='ApiKey',
        ),
    ]
