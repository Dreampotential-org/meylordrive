# Generated by Django 4.0.5 on 2024-05-20 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0012_channel_youtubevideo_channel'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='name',
            field=models.CharField(default=None, max_length=255),
            preserve_default=False,
        ),
    ]