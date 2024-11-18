from rest_framework import serializers
from common.enums.ScopeCategories import Categories_and_Subcategories
from django.utils.translation import gettext_lazy as _
import datetime


class ScopeCategoriesSerializer(serializers.Serializer):
    sub_category = serializers.CharField(max_length=500)
    year = serializers.IntegerField(
        max_value=datetime.datetime.now().year, min_value=2019
    )
    region = serializers.CharField(max_length=300, allow_blank=True)
    for_data_scientist = serializers.BooleanField(default=False)

    class Meta:
        fields = ["for_data_scientist", "year", "region", "sub_category"]
