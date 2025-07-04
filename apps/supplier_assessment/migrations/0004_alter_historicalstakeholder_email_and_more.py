# Generated by Django 4.2.4 on 2025-02-09 17:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("supplier_assessment", "0003_alter_stakeholdergroup_unique_together"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicalstakeholder",
            name="email",
            field=models.EmailField(db_index=True, max_length=500),
        ),
        migrations.AlterField(
            model_name="stakeholder",
            name="email",
            field=models.EmailField(db_index=True, max_length=500),
        ),
    ]
