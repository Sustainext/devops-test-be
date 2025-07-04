# Generated by Django 4.2.4 on 2025-02-12 07:24

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sustainapp', '0014_merge_20250210_0558'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('supplier_assessment', '0006_historicalstakeholder_address_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='stakeholdergroup',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='historicalstakeholdergroup',
            name='name',
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='stakeholdergroup',
            name='name',
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AlterUniqueTogether(
            name='stakeholdergroup',
            unique_together={('name', 'organization', 'created_by')},
        ),
    ]
