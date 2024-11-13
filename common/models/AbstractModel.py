from django.db import models
from common.models.TimeBasedModelMixin import TimeBasedModelMixin


class AbstractModel(TimeBasedModelMixin):
    """
    An abstract model that provides created_at and updated_at fields.
    """

    class Meta:
        abstract = True
