# Generated by Django 4.0.5 on 2024-06-01 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0014_alter_channel_description_alter_channel_subscribers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]