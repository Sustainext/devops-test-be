# Generated by Django 4.2.4 on 2025-04-24 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('optimize', '0008_historicalselectedactivity_unit_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalselectedactivity',
            name='uuid',
            field=models.CharField(default='Default', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='selectedactivity',
            name='uuid',
            field=models.CharField(default='Default', max_length=255),
            preserve_default=False,
        ),
    ]
