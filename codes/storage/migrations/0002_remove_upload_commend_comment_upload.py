# Generated by Django 4.0.5 on 2023-10-27 22:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='upload',
            name='commend',
        ),
        migrations.AddField(
            model_name='comment',
            name='upload',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='storage.upload'),
        ),
    ]