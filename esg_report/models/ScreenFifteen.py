from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from sustainapp.models import Report


class ScreenFifteenModel(AbstractModel, HistoricalModelMixin):
    """
    This model represents the screen fifteen of the ESG report.
    """

    report = models.OneToOneField(
        Report, on_delete=models.CASCADE, related_name="screen_fifteen"
    )
    commitment_statement = models.TextField(
        verbose_name="Company's Commitment to Products and Services",
        help_text="Add a statement about the company's commitment to products and services.",
    )

    product_info_labelling = models.TextField(
        verbose_name="Product and Service Information and Labelling",
        help_text="Add a statement about the company's product and service information and labelling.",
    )

    marketing_practices = models.TextField(
        verbose_name="Company's Marketing Practices",
        help_text="Add a statement about the company's marketing practices.",
    )

    conclusion = models.TextField(
        verbose_name="Conclusion", help_text="Add a conclusion to the report."
    )

    def __str__(self):
        return "Company Report"
