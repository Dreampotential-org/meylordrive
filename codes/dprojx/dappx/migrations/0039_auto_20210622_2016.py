# Generated by Django 2.2.13 on 2021-06-22 20:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xppda', '0038_auto_20210622_2015'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofileinfo',
            name='user_org',
        ),
        migrations.DeleteModel(
            name='Organization',
        ),
    ]
