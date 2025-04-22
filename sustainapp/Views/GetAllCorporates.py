from sustainapp.models import Corporateentity, Userorg
from rest_framework.views import APIView
from sustainapp.Serializers.AllCorporateListSerializer import AllCorporateListSerializer
from rest_framework.response import Response
from rest_framework import status
from datametric.models import RawResponse
from datametric.utils.analyse import filter_by_start_end_dates
from sustainapp.Serializers.CheckAnalysisViewSerializer import (
    CheckAnalysisViewSerializer,
)
class AllCorporateList(APIView):
    """
    If only organizatin is selected : Get all the corporates where the user is linked apart from the selected organization's corporates.
    If both organization and corporate are selected : Get all the corporates where the user is linked apart from the selected corporate.
    """
    def get(self, request):
        # Retrieve the 'organization_id' from query parameters
        serializer = CheckAnalysisViewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        from_date = serializer.validated_data["start"]
        to_date = serializer.validated_data["end"]

        organization_id = serializer.validated_data["organisation"].id
        corporate = serializer.validated_data.get("corporate", None)

        try:
            corporates = self._get_corporates(
                request.user, organization_id, corporate, from_date, to_date
            )
        except ValueError:
            return Response(
                {"error": "Invalid organization_id"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AllCorporateListSerializer(corporates, many=True)

        for corporate in serializer.data:
            corporate_id = corporate['id']

            emission_data = (
                RawResponse.objects.filter(locale__corporateentity=corporate_id)
                .filter(filter_by_start_end_dates(from_date, to_date))
                .exists()
            )
            corporate['emission_data'] = emission_data

        return Response(serializer.data)

    def _get_corporates(self, user, organization_id, corporate, from_date, to_date):
        if corporate:
            return Corporateentity.objects.exclude(id=corporate.id).filter(
                id__in=user.corps.values_list("id", flat=True)
            )

        return Corporateentity.objects.exclude(organization_id=organization_id).filter(
            id__in=user.corps.values_list("id", flat=True)
        )