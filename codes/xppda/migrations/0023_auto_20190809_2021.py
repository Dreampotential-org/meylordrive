# Generated by Django 2.2.3 on 2019-08-09 20:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xppda', '0022_videoupload_source'),
    ]

    operations = [
        migrations.RenameField(
            model_name='videoupload',
            old_name='uploaded_at',
            new_name='created_at',
        ),
    ]
