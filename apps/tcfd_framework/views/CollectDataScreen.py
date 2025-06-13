from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.tcfd_framework.serializers.CollectSerializer import CollectBasicSerializer
from datametric.models import DataPoint


class CollectDataScreen(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.climate_slugs = {
            "gri-economic-climate_related_risks-202-2a-physical_risk": "TypeofRisk",
            "gri-economic-climate_related_risks-202-2a-transition_risk": "TypeofRisk",
            "gri-economic-climate_related_risks-202-2a-other_risk": "TypeofRiskoth",
        }
        self.opportunities_slugs = {
            "gri-economic-climate_realted_opportunities-202-2a-report": "TypeofOpportunities",
        }

    def get(self, request, *args, **kwargs):
        serializer = CollectBasicSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        organization = serializer.validated_data["organization"]
        corporate = serializer.validated_data.get("corporate", None)
        location = serializer.validated_data.get("location", None)
        year = serializer.validated_data["year"]
        climate_filters = {
            "path__slug__in": list(self.climate_slugs.keys()),
            "organization": organization,
            "year": year,
            "data_metric__name__in": list(set(self.climate_slugs.values())),
        }
        if corporate:
            climate_filters["corporate"] = corporate
        if location:
            climate_filters["location"] = location

        climate_dps = DataPoint.objects.filter(**climate_filters).values_list(
            "value", flat=True
        )
        opportunities_filters = {
            "path__slug__in": list(self.opportunities_slugs.keys()),
            "organization": organization,
            "year": year,
            "data_metric__name__in": list(set(self.opportunities_slugs.values())),
        }
        if corporate:
            opportunities_filters["corporate"] = corporate
        if location:
            opportunities_filters["location"] = location

        opportunities_dps = DataPoint.objects.filter(
            **opportunities_filters
        ).values_list("value", flat=True)

        return Response(
            data={
                "message": "Data from Climate Related Risks and Climate Related Opportunities collect section",
                "data": {
                    "climate_data": climate_dps,
                    "opportunities_data": opportunities_dps,
                },
            },
            status=status.HTTP_200_OK,
        )
