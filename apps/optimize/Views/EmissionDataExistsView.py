from rest_framework.views import APIView
from rest_framework.response import Response
from datametric.models import EmissionAnalysis
from sustainapp.models import Location
from apps.optimize.Serializers.EmissionDataExistsSerializer import (
    EmissionDataRequestSerializer,
)
from rest_framework import status


class EmissionDataExistsView(APIView):
    def post(self, request):
        serializer = EmissionDataRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        organization = data.get("organization")
        corporate = data.get("corporate")
        year = data["year"]

        if organization and not corporate:
            locations = Location.objects.filter(
                corporateentity__organization_id=organization
            ).values_list("id", flat=True)

            emission_data = EmissionAnalysis.objects.filter(
                year=year,
                raw_response__locale__in=locations,
            ).exists()

            return Response({"exists": emission_data})

        elif corporate:
            locations = Location.objects.filter(corporateentity_id=corporate)

            emission_data = EmissionAnalysis.objects.filter(
                year=year,
                raw_response__locale__in=locations,
            ).exists()

            return Response({"exists": emission_data})

        return Response({"exists": False})
