from django.db import models
from common.models.AbstractModel import AbstractModel
from sustainapp.models import Organization, Corporateentity
from django.contrib.auth import get_user_model
from common.models.HistoricalModel import HistoricalModelMixin

User = get_user_model()


class Scenerio(AbstractModel, HistoricalModelMixin):
    """
    Model for storing scenario data.
    """

    scenario_by_choices = (
        ("corporate", "corporate"),
        ("organization", "organization"),
    )

    name = models.CharField(max_length=255)
    base_year = models.IntegerField()
    target_year = models.IntegerField()
    scenario_by = models.CharField(
        max_length=255, choices=scenario_by_choices, default="organization"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, name="organization"
    )
    corporate = models.ForeignKey(
        Corporateentity,
        on_delete=models.CASCADE,
        name="corporate",
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_by_scenerio"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="updated_by_scenerio"
    )

    def __str__(self):
        return f"{self.name} - {self.created_by.username}"
