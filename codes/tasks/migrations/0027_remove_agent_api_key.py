# Generated by Django 4.0.5 on 2023-12-05 01:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0026_statsentry_agent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agent',
            name='api_key',
        ),
    ]