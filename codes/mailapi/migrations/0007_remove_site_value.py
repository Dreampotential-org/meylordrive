# Generated by Django 4.0.5 on 2023-12-30 00:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mailapi', '0006_site'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='site',
            name='value',
        ),
    ]