from django.db import models
from common.models.AbstractModel import AbstractModel
from sustainapp.models import Organization, Corporateentity
from django.contrib.auth import get_user_model

User = get_user_model()


class Scenerio(AbstractModel):
    """
    Model for storing scenario data.
    """

    name = models.CharField(max_length=255)
    base_year = models.IntegerField()
    target_year = models.IntegerField()
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
