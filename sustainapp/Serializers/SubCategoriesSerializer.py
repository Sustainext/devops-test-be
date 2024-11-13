from rest_framework import serializers
from common.enums.ScopeCategories import Categories_and_Subcategories
from django.utils.translation import gettext_lazy as _


class SubCategoriesSerializer(serializers.Serializer):
    categories = serializers.CharField(max_length=50)

    class Meta:
        fields = ["categories"]

    def validate(self, attrs):
        categories = attrs.get("categories", None)
        if categories and categories not in Categories_and_Subcategories.keys():
            raise serializers.ValidationError(
                detail=_("Invalid Category Given"), code=_("Invalid Parameters")
            )

        return super().validate(attrs)
