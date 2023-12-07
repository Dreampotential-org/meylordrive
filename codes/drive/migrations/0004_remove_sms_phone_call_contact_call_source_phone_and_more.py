# Generated by Django 4.0.5 on 2023-11-29 01:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0003_contact_home_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sms',
            name='phone',
        ),
        migrations.AddField(
            model_name='call',
            name='contact',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='drive.contact'),
        ),
        migrations.AddField(
            model_name='call',
            name='source_phone',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='drive.phone'),
        ),
        migrations.AddField(
            model_name='sms',
            name='source_phone',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='drive.phone'),
        ),
        migrations.AlterField(
            model_name='call',
            name='phone_number',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='call_phone_number', to='drive.phone'),
        ),
    ]