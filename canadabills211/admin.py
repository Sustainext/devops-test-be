from django.contrib import admin
from .models.CanadaBillS211 import IdentifyingInformation, AnnualReport


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

@admin.register(AnnualReport)
class AnnualReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "organization",
        "corporate",
        "year",
        "steps_taken_1",
        "structure_3",
        "policies_in_place_6",
        "risk_identified_8",
        "measures_remediate_activaties_11",
        "training_provided_15",
        "policies_procedures_assess_17",
    )
    list_filter = (
        "year",
        "client",
        "organization",
        "corporate",
        "policies_in_place_6",
        "risk_identified_8",
        "training_provided_15",
    )
    search_fields = ("client__name", "organization__name", "corporate__name", "year")
    ordering = ("-year",)

    fieldsets = (
        (
            "General Information",
            {"fields": ("client", "user", "organization", "corporate", "year")},
        ),
        (
            "Screen 1",
            {
                "fields": (
                    "steps_taken_1",
                    "steps_taken_description_1",
                    "additional_information_2",
                )
            },
        ),
        (
            "Screen 2",
            {
                "fields": (
                    "structure_3",
                    "categorization_4",
                    "additional_information_entity_5",
                )
            },
        ),
        (
            "Screen 3",
            {
                "fields": (
                    "policies_in_place_6",
                    "elements_implemented_6_1",
                    "additional_info_policies_7",
                )
            },
        ),
        (
            "Screen 4",
            {
                "fields": (
                    "risk_identified_8",
                    "risk_aspects_8_1",
                    "risk_aspects_description_8_1",
                    "risk_activaties_9",
                    "risk_activaties_description_9",
                    "additional_info_entity_10",
                )
            },
        ),
        (
            "Screen 5",
            {
                "fields": (
                    "measures_remediate_activaties_11",
                    "remediation_measures_taken_11_1",
                    "remediation_measures_taken_description_11_1",
                    "remediation_measures_12",
                )
            },
        ),
        (
            "Screen 6",
            {
                "fields": (
                    "measures_taken_loss_income_13",
                    "additional_info_loss_income_14",
                )
            },
        ),
        (
            "Screen 7",
            {
                "fields": (
                    "training_provided_15",
                    "training_mandatory_15_1",
                    "additional_info_training_16",
                )
            },
        ),
        (
            "Screen 8",
            {
                "fields": (
                    "policies_procedures_assess_17",
                    "assessment_method_17_1",
                    "assessment_method_description_17_1",
                    "additional_info_assessment_18",
                )
            },
        ),
    )
