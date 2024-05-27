from rest_framework.views import APIView
from sustainapp.Serializers.SubCategoriesSerializer import SubCategoriesSerializer
from rest_framework.permissions import IsAuthenticated
from common.enums.ScopeCategories import Categories_and_Subcategories
from rest_framework.response import Response
from rest_framework import status


class SubCategoriesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = SubCategoriesSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        categories = serializer.validated_data["categories"]
        data = {
            "sub_categories": Categories_and_Subcategories[categories],
            "status": status.HTTP_200_OK,
        }
        return Response(data=data, status=status.HTTP_200_OK)
