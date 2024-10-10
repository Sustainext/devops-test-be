from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel


class RecycledInputMaterials(AbstractAnalysisModel, AbstractModel):
    """
    Model for Recycled Input Materials
    """

    recycled_material = models.CharField(max_length=100)
    type_of_recycled_material = models.CharField(max_length=100)
    total_weight_or_volume = models.DecimalField(max_digits=20, decimal_places=6)
    amount_of_material_recycled = models.DecimalField(max_digits=20, decimal_places=6)
    amount_of_recycled_input_material_used = models.DecimalField(
        max_digits=20, decimal_places=6
    )
    unit_material_recycled = models.CharField(max_length=100)
    unit_input_material_used = models.CharField(max_length=100)
    index = models.PositiveIntegerField()
