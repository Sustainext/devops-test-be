from rest_framework import serializers
from common.enums.ScopeCategories import Categories_and_Subcategories
from django.utils.translation import gettext_lazy as _
import datetime


class ScopeCategoriesSerializer(serializers.Serializer):
    category = serializers.CharField(max_length=50)
    sub_category = serializers.CharField(max_length=500)
    year = serializers.IntegerField(
        max_value=datetime.datetime.now().year, min_value=2019
    )
    region = serializers.CharField(max_length=300, allow_blank=True)

    class Meta:
        fields = ["category", "year", "region", "sub_category"]

    def validate(self, attrs):
        category = attrs.get("category", None)
        sub_category = attrs.get("sub_category", None)
        if (
            category
            and (category not in list(Categories_and_Subcategories.keys()))
            and sub_category not in Categories_and_Subcategories.get(category, dict())
        ):
            raise serializers.ValidationError(
                detail=_("Invalid Category Given"), code=_("Invalid Parameters")
            )
        return super().validate(attrs)
