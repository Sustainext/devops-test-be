# Generated by Django 4.2.4 on 2025-06-12 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tcfd_framework', '0005_rename_corporate_entity_historicalselecteddisclosures_corporate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicaltcfdreportinginformation',
            name='status',
            field=models.BooleanField(default=False, help_text='Indicates if the reporting information is complete'),
        ),
        migrations.AddField(
            model_name='tcfdreportinginformation',
            name='status',
            field=models.BooleanField(default=False, help_text='Indicates if the reporting information is complete'),
        ),
    ]
