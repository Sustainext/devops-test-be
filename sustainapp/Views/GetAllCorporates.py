from sustainapp.models import Corporateentity
from rest_framework.views import APIView
from sustainapp.Serializers.AllCorporateListSerializer import AllCorporateListSerializer
from rest_framework.response import Response

class AllCorporatelist(APIView):
    def get(self, request):
        corporates = Corporateentity.objects.all()
        serializer = AllCorporateListSerializer(corporates, many=True)
        return Response(serializer.data)