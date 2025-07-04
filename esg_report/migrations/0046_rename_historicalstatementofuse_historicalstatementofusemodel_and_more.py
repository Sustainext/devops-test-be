# Generated by Django 4.2.4 on 2024-10-26 09:52

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("sustainapp", "0002_remove_userorg_organization_userorg_organization"),
        ("esg_report", "0045_statementofuse_historicalstatementofuse"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="HistoricalStatementOfUse",
            new_name="HistoricalStatementOfUseModel",
        ),
        migrations.RenameModel(
            old_name="StatementOfUse",
            new_name="StatementOfUseModel",
        ),
        migrations.AlterModelOptions(
            name="historicalstatementofusemodel",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical statement of use model",
                "verbose_name_plural": "historical statement of use models",
            },
        ),
    ]
