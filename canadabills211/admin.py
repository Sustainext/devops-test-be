from django.contrib import admin
from .models import IdentifyingInformation


@admin.register(IdentifyingInformation)
class IdentifyingInformationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "user",
        "organization",
        "corporate",
        "year",
        "report_purpose_1",
        "reporting_legal_name_2",
        "financial_reporting_year_from_3",
        "financial_reporting_year_to_3",
        "is_revised_version_4",
        "original_report_date_4_1",
        "business_number_5",
        "is_joint_report_6",
        "subject_to_supply_chain_legislation_7",
        "country_10",
        "province_or_territory_10_1",
    )
    list_filter = ("client", "year", "organization", "corporate")
    search_fields = ("reporting_legal_name_2", "business_number_5", "country_10")
    ordering = ("-year",)

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("client", "user", "organization", "corporate", "year")},
        ),
        (
            "Screen 1: Reporting Details",
            {
                "fields": (
                    "report_purpose_1",
                    "reporting_legal_name_2",
                    "financial_reporting_year_from_3",
                    "financial_reporting_year_to_3",
                )
            },
        ),
        (
            "Screen 2: Revision Details",
            {
                "fields": (
                    "is_revised_version_4",
                    "original_report_date_4_1",
                    "changes_description_4_2",
                )
            },
        ),
        (
            "Screen 3: Business Numbers",
            {
                "fields": (
                    "business_number_5",
                    "is_joint_report_6",
                    "legal_name_and_business_numbers_6_1_2",
                )
            },
        ),
        (
            "Screen 4: Supply Chain Legislation",
            {
                "fields": (
                    "subject_to_supply_chain_legislation_7",
                    "applicable_laws_7_1",
                    "other_laws_description_7_1",
                )
            },
        ),
        ("Screen 5: Categorizations", {"fields": ("categorizations_8",)}),
        (
            "Screen 6: Sectors or Industries",
            {
                "fields": (
                    "sectors_or_industries_9",
                    "sectors_or_industries_description_9",
                )
            },
        ),
        (
            "Screen 7: Location",
            {"fields": ("country_10", "province_or_territory_10_1")},
        ),
    )
