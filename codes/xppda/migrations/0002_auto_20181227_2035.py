# Generated by Django 2.1.4 on 2018-12-27 20:35

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('xppda', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofileinfo',
            name='portfolio_site',
        ),
        migrations.RemoveField(
            model_name='userprofileinfo',
            name='profile_pic',
        ),
        migrations.AlterField(
            model_name='userprofileinfo',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, unique=True),
        ),
    ]
