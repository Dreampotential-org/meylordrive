# Generated by Django 2.2.20 on 2022-06-08 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0008_auto_20220608_2307'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='alive',
            field=models.BooleanField(default=False),
        ),
    ]