from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from sustainapp.models import Location
from sustainapp.Serializers.CorporateCheckSerializer import GetCorporateSerializer
from sustainapp.Serializers.GetLocationSerializer import GetLocationSerializer
from rest_framework.response import Response


class GetLocationAsPerCorporate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = GetCorporateSerializer(
            data=request.query_params, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        corporate = serializer.validated_data["corporate"]
        locations = Location.objects.filter(corporateentity=corporate)
        serializer = GetLocationSerializer(locations, many=True)
        return Response(serializer.data)
