# Generated by Django 4.2.4 on 2024-11-25 06:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_alter_customuser_work_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='department',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='designation',
        ),
    ]
