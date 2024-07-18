from typing import Any
from django.core.management.base import BaseCommand
from datametric.models import DataPoint, RawResponse, Path, DataMetric
from sustainapp.models import Organization, Corporateentity, Location


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        try:
            k = RawResponse.objects.filter(id__range=[280, 282]).order_by("id")
            for i in k:
                l = Location.objects.get(name=i.location)
                i.locale = None
                i.save()
            print("done with the updation")
        except Exception as e:
            print("Error : ", e)
