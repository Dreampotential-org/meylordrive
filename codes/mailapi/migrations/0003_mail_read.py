# Generated by Django 4.0.5 on 2023-12-07 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailapi', '0002_mail_body'),
    ]

    operations = [
        migrations.AddField(
            model_name='mail',
            name='read',
            field=models.BooleanField(default=False),
        ),
    ]
