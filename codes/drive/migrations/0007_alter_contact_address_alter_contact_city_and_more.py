# Generated by Django 4.0.5 on 2023-12-08 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0006_alter_contact_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='address',
            field=models.CharField(max_length=2550),
        ),
        migrations.AlterField(
            model_name='contact',
            name='city',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='name',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='price',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='state',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='url',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
