from django.db import models
from sustainapp.models import Report
from common.models.AbstractModel import AbstractModel


class EsgCustomReport(AbstractModel):
    report = models.OneToOneField(Report, on_delete=models.CASCADE)
    section = models.JSONField(default=dict)
    sub_section = models.JSONField(default=dict)
    include_management_material_topics = models.BooleanField(default=False)
    include_content_index = models.BooleanField(default=False)

    def __str__(self):
        return f"Custom Report for {self.report.name}"
