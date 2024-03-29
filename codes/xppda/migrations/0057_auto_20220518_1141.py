# Generated by Django 2.2.16 on 2022-05-18 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xppda', '0056_userlead'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='address',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='city',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='state',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='userlead',
            name='email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='userlead',
            name='name',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userlead',
            name='website',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
