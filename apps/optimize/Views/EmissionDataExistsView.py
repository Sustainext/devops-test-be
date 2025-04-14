from rest_framework.views import APIView
from rest_framework.response import Response
from datametric.models import EmissionAnalysis
from sustainapp.models import Location


class EmissionDataExistsView(APIView):
    def get(self, request):
        organization = request.GET.get("organization")
        corporate = request.GET.get("corporate")
        year = request.GET.get("year")

        if not year:
            return Response("Year is required.")

        if not any([organization, corporate]):
            return Response("At least one of organization, corporate is required.")

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

        else:
            return Response({"exists": False})
