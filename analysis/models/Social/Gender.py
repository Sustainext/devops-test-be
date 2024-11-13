from django.db import models
from common.models.AbstractModel import AbstractModel


class Gender(AbstractModel):
    gender = models.CharField(max_length=50)

    def __str__(self):
        return self.gender
