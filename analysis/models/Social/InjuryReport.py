from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel
from sustainapp.models import Organization, Corporateentity, Location

INJURIES_FOR_WHOM_CHOICES = (
    (
        "the_number_of_injuries_for_all_employees",
        "The number of injuries for all employees",
    ),
    (
        "the_number_of_injuries_for_workers_who_are_not_employees_but_whose_work_and_workplace_is_controlled_by_the_organization",
        "The Number of Injuries for workers who are not employees but whose work and workplace is controlled by the organization",
    ),
)


class InjuryReport(AbstractModel, AbstractAnalysisModel):
    table_name = models.CharField(max_length=120, choices=INJURIES_FOR_WHOM_CHOICES)
    employee_category = models.CharField(
        max_length=500,
        help_text="Indicate if the report is for employees or non-employees controlled by the organization.",
    )
    fatalities = models.PositiveIntegerField(
        help_text="Number of fatalities as a result of work-related injury"
    )
    high_consequence_injuries = models.PositiveIntegerField(
        help_text="Number of high-consequence work-related injuries (excluding fatalities)"
    )
    recordable_injuries = models.PositiveIntegerField(
        help_text="Number of recordable work-related injuries"
    )
    injury_types = models.TextField(help_text="Main types of work-related injury")
    hours_worked = models.PositiveIntegerField(help_text="Number of hours worked")
    index = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.employee_category} - Injuries Report"

    class Meta:
        verbose_name_plural = "Injury Reports"
