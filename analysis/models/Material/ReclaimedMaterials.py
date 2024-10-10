from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.AbstactAnalysisModel import AbstractAnalysisModel


class ReclaimedMaterials(AbstractModel, AbstractAnalysisModel):
    type_of_product_sold = models.CharField(max_length=100)
    product_classification = models.CharField(max_length=100)
    product_code = models.CharField(max_length=100)
    product_name = models.CharField(max_length=100)
    amount_of_product_sold = models.DecimalField(max_digits=10, decimal_places=6)
    product_sold_unit = models.CharField(max_length=100)
    recycled_material_used = models.CharField(max_length=100)
    type_of_recycled_material_used = models.CharField(max_length=100)
    amount_of_recycled_material_used = models.DecimalField(
        max_digits=10, decimal_places=6
    )
    recycled_material_used_unit = models.CharField(max_length=100)
    data_collection_method = models.CharField(max_length=100)
    index = models.PositiveIntegerField()
