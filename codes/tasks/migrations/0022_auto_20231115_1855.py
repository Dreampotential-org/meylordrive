# Generated by Django 3.2.23 on 2023-11-15 13:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0021_agent'),
    ]

    operations = [
        migrations.AddField(
            model_name='org',
            name='about',
            field=models.CharField(blank=True, default=None, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='org',
            name='address',
            field=models.CharField(blank=True, default=None, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='org',
            name='email',
            field=models.CharField(blank=True, default=None, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='org',
            name='image',
            field=models.CharField(blank=True, default='https://www.iconfinder.com/icons/636895/users_avatar_group_human_people_profile_team_icon', max_length=500),
        ),
        migrations.AddField(
            model_name='org',
            name='meta_attributes',
            field=models.CharField(default='some_default_value', max_length=256, unique=True),
        ),
        migrations.AddField(
            model_name='org',
            name='phone_number',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='agent',
            name='api_key',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='tasks.apikey'),
        ),
        migrations.CreateModel(
            name='AgentSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('ended_at', models.DateTimeField(auto_now_add=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.agent')),
            ],
        ),
    ]
