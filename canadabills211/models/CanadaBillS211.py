from django.db import models
from common.models.AbstractModel import AbstractModel
from sustainapp.models import Organization, Corporateentity
from authentication.models import CustomUser, Client

"""
Once you create models here, you need to regiester them in sustainapp.ModelsForSustainapp.__init__.py
"""


class IdentifyingInformation(AbstractModel):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="Identifying_information_client",
        default=Client.get_default_client,
    )
    # user id
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.DO_NOTHING,
        related_name="Idnetifying_Information_User",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="Idnetifying_Information_Organization",
    )
    corporate = models.ForeignKey(
        Corporateentity,
        on_delete=models.CASCADE,
        related_name="Idnetifying_Information_Corporate",
        null=True,
    )
    year = models.IntegerField(
        help_text="Year of the financial reporting year",
    )
    # screen 1
    report_purpose_1 = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="1. This report is for which of the following?",
    )
    reporting_legal_name_2 = models.CharField(
        max_length=128,
        blank=False,
        null=True,
        help_text="2.Legal name of reporting entity",
    )
    financial_reporting_year_from_3 = models.DateField(
        blank=False, null=True, help_text="3.Financial reporting year from"
    )
    financial_reporting_year_to_3 = models.DateField(
        blank=False, null=True, help_text="3.Financial reporting year to"
    )
    # screen 2
    is_revised_version_4 = models.CharField(
        max_length=16,
        blank=False,
        null=True,
        help_text="4.Is this a revised version of a report already submitted this reporting year?",
    )
    original_report_date_4_1 = models.DateField(
        blank=True,
        null=True,
        help_text="4.1 If yes, identify the date the original report was submitted.",
    )
    changes_description_4_2 = models.TextField(
        max_length=1500,
        blank=True,
        null=True,
        help_text="4.2 Describe the changes made to the original report, including by listing the questions or sections that were revised (1,500 character limit)",
    )
    # screen 3
    business_number_5 = models.BigIntegerField(
        blank=True, null=True, help_text="5. Business Number(s)"
    )
    is_joint_report_6 = models.CharField(
        max_length=16, blank=False, null=True, help_text="6. Is this a joint report?"
    )
    legal_name_and_business_numbers_6_1_2 = models.JSONField(
        blank=True,
        null=True,
        help_text="6.1 & 6.2 If yes, identify the legal name and business number(s) of each entity covered by this report",
    )
    # screen 4
    subject_to_supply_chain_legislation_7 = models.CharField(
        max_length=16,
        blank=False,
        null=True,
        help_text="7. Is the entity also subject to reporting requirements under supply chain legislation in another jurisdiction",
    )
    applicable_laws_7_1 = models.JSONField(
        blank=True, null=True, help_text="7.1 If yes, indicate the applicable law(s)"
    )
    other_laws_description_7_1 = models.TextField(
        max_length=1500,
        blank=True,
        null=True,
        help_text="7.1 Description for applicable law(s)",
    )
    # screen 5
    categorizations_8 = models.JSONField(
        null=True,
        help_text="8. Which of the following categorizations applies to the entity?",
    )
    # scren 6
    sectors_or_industries_9 = models.JSONField(
        blank=False,
        null=True,
        help_text="9. Which of the following sectors or industries does the entity operate in?",
    )
    sectors_or_industries_description_9 = models.TextField(
        max_length=1500,
        blank=True,
        null=True,
        help_text="9. Other sector or industries",
    )
    # screen 7
    country_10 = models.CharField(
        max_length=128,
        blank=False,
        null=True,
        help_text="10. Country headquarted or principally located?",
    )
    province_or_territory_10_1 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="10.1 If in Canada: In which province or territory is the entity headquartered or principally located?",
    )

    def __str__(self):
        return f"{self.id}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["client", "organization", "corporate", "year"],
                name="unique_identifying_information",
            )
        ]
