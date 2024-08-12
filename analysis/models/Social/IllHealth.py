from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel


class IllHealthReport(
    AbstractModel,
):
    TABLE_NAME_CHOICES = [
        ("employees", "Employees"),
        ("non_employees", "Non-Employees (Controlled by Organization)"),
    ]
    table_name = models.CharField(
        max_length=200,
        choices=TABLE_NAME_CHOICES,
    )
    employee_category = models.CharField(
        max_length=500,
        choices=TABLE_NAME_CHOICES,
        help_text="Indicate if the report is for employees or non-employees controlled by the organization.",
    )
    fatalities_due_to_ill_health = models.PositiveIntegerField(
        help_text="Number of fatalities as a result of work-related ill health"
    )
    recordable_ill_health_cases = models.PositiveIntegerField(
        help_text="Number of cases of recordable work-related ill health"
    )
    types_of_ill_health = models.TextField(
        help_text="Main types of work-related ill health"
    )

    def __str__(self):
        return f"{self.employee_category()} - Ill Health Report"

    class Meta:
        verbose_name_plural = "Ill Health Reports"
