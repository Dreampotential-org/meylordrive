# Generated by Django 4.0.5 on 2023-11-29 21:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0004_remove_sms_phone_call_contact_call_source_phone_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contact',
            old_name='owner_phone_other',
            new_name='phone_other',
        ),
    ]
