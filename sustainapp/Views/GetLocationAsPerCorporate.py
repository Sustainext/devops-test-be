from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from sustainapp.models import Location, Corporateentity, Organization
from sustainapp.Serializers.CorporateCheckSerializer import GetCorporateSerializer
from sustainapp.Serializers.GetLocationSerializer import GetLocationSerializer
from sustainapp.Serializers.CheckOrgCorpSerializer import  CheckOrgCoprSerializer
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

class GetLocationAsPerOrgOrCorp(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = CheckOrgCoprSerializer(data = request.query_params)
        serializer.is_valid(raise_exception=True)
        organization = serializer.validated_data["organization"]
        corporate = serializer.validated_data.get("corporate")

        if corporate:
            locations = Location.objects.filter(corporateentity__id=corporate.id)
        else :
            locations = Location.objects.filter(corporateentity__organization__id=organization.id)

        res = [{"location_id" : loc.id, "location_name" : loc.name} for loc in locations]
        return Response(res)
