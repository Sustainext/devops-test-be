# Generated by Django 4.2.4 on 2025-05-09 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('optimize', '0017_calculatedresult_uuid_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalscenerio',
            name='description',
            field=models.TextField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='scenerio',
            name='description',
            field=models.TextField(blank=True, max_length=512, null=True),
        ),
    ]
