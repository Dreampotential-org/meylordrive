# Generated by Django 2.2.16 on 2022-10-25 22:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xppda', '0059_userprofileinfo_notes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofileinfo',
            name='user_org',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='xppda.Organization'),
        ),
    ]