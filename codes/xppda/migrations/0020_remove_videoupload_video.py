# Generated by Django 2.2.3 on 2019-07-19 13:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xppda', '0019_videoupload_video'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='videoupload',
            name='video',
        ),
    ]
