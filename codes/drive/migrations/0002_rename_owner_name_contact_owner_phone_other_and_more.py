# Generated by Django 4.0.5 on 2023-11-22 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contact',
            old_name='owner_name',
            new_name='owner_phone_other',
        ),
        migrations.RemoveField(
            model_name='contact',
            name='owner_phone',
        ),
        migrations.AddField(
            model_name='contact',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
