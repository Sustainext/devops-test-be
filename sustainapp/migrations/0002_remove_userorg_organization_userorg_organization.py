# Generated by Django 5.1.1 on 2024-10-26 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sustainapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userorg',
            name='organization',
        ),
        migrations.AddField(
            model_name='userorg',
            name='organization',
            field=models.ManyToManyField(related_name='userorg_organization', to='sustainapp.organization'),
        ),
    ]
