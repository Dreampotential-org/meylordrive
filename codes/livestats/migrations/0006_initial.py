# Generated by Django 4.0.5 on 2023-11-29 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('livestats', '0005_delete_websocketconnection'),
    ]

    operations = [
        migrations.CreateModel(
            name='JsError',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True, null=True)),
                ('url', models.TextField(blank=True, null=True)),
                ('lineNo', models.TextField(blank=True, null=True)),
                ('columnNo', models.TextField(blank=True, null=True)),
                ('error_msg', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WebSocketConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_group', models.CharField(max_length=255)),
                ('connection_time', models.DateTimeField()),
            ],
        ),
    ]