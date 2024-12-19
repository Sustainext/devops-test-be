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
        max_length=2048,
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


class AnnualReport(AbstractModel):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="Annual_report_client",
        default=Client.get_default_client,
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.DO_NOTHING, related_name="Annaul_report"
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="Annual_report_Organization",
    )
    corporate = models.ForeignKey(
        Corporateentity,
        on_delete=models.CASCADE,
        related_name="Annual_report_Corporate",
        null=True,
    )
    year = models.IntegerField(
        help_text="Year of the financial reporting year",
    )
    # screen 1
    steps_taken_1 = models.JSONField(
        null=True,
        blank=False,
        help_text="1. What steps has the entity taken in the previous financial year to prevent and reduce the risk that forced labour or child labour is used at any step of the production of goods in Canada or elsewhere by the entity or of goods imported into Canada by the entity? Select all that apply",
    )
    steps_taken_description_1 = models.TextField(
        null=True, blank=True, help_text="1. Other, please specify"
    )
    additional_information_2 = models.TextField(
        null=True,
        blank=False,
        help_text="2. Please provide additional information describing the steps taken (if applicable)",
    )
    # screen 2
    structure_3 = models.CharField(
        max_length=255,
        null=True,
        blank=False,
        help_text="3.Which of the following accurately describes the entity’s structure?",
    )
    categorization_4 = models.JSONField(
        null=True,
        blank=False,
        help_text="4. Which of the following categorizations applies to the entity?",
    )
    additional_information_entity_5 = models.TextField(
        null=True,
        blank=False,
        help_text="5. Please provide additional information on the entity’s structure, activities and supply chains",
    )
    # screen 3
    policies_in_place_6 = models.CharField(
        max_length=16,
        null=True,
        blank=False,
        help_text="6.Does the entity currently have policies and due diligence processes in place related to forced labour and/or child labour?",
    )
    elements_implemented_6_1 = models.JSONField(
        null=True,
        blank=True,
        help_text="6.1 If yes, which of the following elements of the due diligence process has the entity implemented in relation to forced labour and/or child labour?Select all that apply",
    )
    additional_info_policies_7 = models.TextField(
        null=True,
        blank=False,
        help_text="7. Please provide additional information on the entity’s policies and due diligence processes in relation to forced labour and child labour (if applicable)",
    )
    # screen 4
    risk_identified_8 = models.CharField(
        max_length=255,
        null=True,
        blank=False,
        help_text="8.Has the entity identified parts of its activities and supply chains that carry a risk of forced labour or child labour being used?",
    )
    risk_aspects_8_1 = models.JSONField(
        null=True,
        blank=False,
        help_text="8.1 If yes, has the entity identified forced labour or child labour risks related to any of the following aspects of its activities and supply chains? Select all that apply",
    )
    risk_aspects_description_8_1 = models.TextField(
        null=True, blank=True, help_text="8.1 Other, please specify"
    )
    risk_activaties_9 = models.JSONField(
        null=True,
        blank=False,
        help_text="9. Has the entity identified forced labour or child labour risks in its activities and supply chains related to any of the following sectors and industries? Select all that apply",
    )
    risk_activaties_description_9 = models.TextField(
        null=True, blank=True, help_text="9. Other, please specify"
    )
    additional_info_entity_10 = models.TextField(
        null=True,
        blank=False,
        help_text="10. Please provide additional information on the parts of the entity’s activities and supply chains that carry a risk of forced labour or child labour being used, as well as the steps that the entity has taken to assess and manage that risk (if applicable)",
    )
    # screen 5
    measures_remediate_activaties_11 = models.TextField(
        null=True,
        blank=False,
        help_text="11. Has the entity taken any measures to remediate any forced labour or child labour in its activities and supply chains?",
    )
    remediation_measures_taken_11_1 = models.JSONField(
        null=True,
        blank=False,
        help_text="11.1 If yes, which remediation measures has the entity taken? Select all that apply",
    )
    remediation_measures_taken_description_11_1 = models.TextField(
        null=True, blank=True, help_text="11.1 Other, please specify"
    )
    remediation_measures_12 = models.TextField(
        null=True,
        blank=False,
        help_text="12. Please provide additional information on any measures the entity has taken to remediate any forced labour or child labour (if applicable)",
    )
    # screen 6
    measures_taken_loss_income_13 = models.CharField(
        max_length=1500,
        null=True,
        blank=False,
        help_text="13. Has the entity taken any measures to remediate the loss of income to the most vulnerable families that results from any measure taken to eliminate the use of forced labour or child labour in its activities and supply chains?",
    )
    additional_info_loss_income_14 = models.TextField(
        null=True,
        blank=False,
        help_text="14. Please provide additional information on any measures the entity has taken to remediate the loss of income to the most vulnerable families that results from any measure taken to eliminate the use of forced labour or child labour in its activities and supply chains (if applicable)",
    )
    # screen 7
    training_provided_15 = models.CharField(
        max_length=255,
        null=True,
        blank=False,
        help_text="15. Does the entity currently provide training to employees on forced labour and/or child labour?",
    )
    training_mandatory_15_1 = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="15.1 If yes, is the training mandatory?",
    )
    additional_info_training_16 = models.TextField(
        null=True,
        blank=False,
        help_text="16. Please provide additional information on any measures the entity has taken to remediate the loss of income to the most vulnerable families that results from any measure taken to eliminate the use of forced labour or child labour in its activities and supply chains (if applicable)",
    )
    # screen 8
    policies_procedures_assess_17 = models.CharField(
        max_length=16,
        null=True,
        blank=False,
        help_text="17. Does the entity currently have policies and procedures in place to assess its effectiveness in ensuring that forced labour and child labour are not being used in its activities and supply chains?",
    )
    assessment_method_17_1 = models.JSONField(
        null=True,
        blank=True,
        help_text="17.1 If yes, what method does the entity use to assess its effectiveness? Select all that apply",
    )
    assessment_method_description_17_1 = models.TextField(
        null=True, blank=True, help_text="17.1 Other, please specify"
    )
    additional_info_assessment_18 = models.TextField(
        null=True,
        blank=False,
        help_text="18. Please provide additional information on how the entity assesses its effectiveness in ensuring that forced labour and child labour are not being used in its activities and supply chains (if applicable)",
    )

    def __str__(self):
        return f"{self.id}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["client", "organization", "corporate", "year"],
                name="unique_annual_report",
            )
        ]
