from sustainapp.models import Corporateentity
from rest_framework.views import APIView
from sustainapp.Serializers.AllCorporateListSerializer import AllCorporateListSerializer
from rest_framework.response import Response
from rest_framework import status

class AllCorporateList(APIView):
    def get(self, request):
        # Retrieve the 'organization_id' from query parameters
        organization_id = request.query_params.get('organization_id')

        if organization_id:
            try:
                organization_id = int(organization_id)  # Convert to integer
                corporates = Corporateentity.objects.exclude(organization_id=organization_id)
            except ValueError:
                return Response({"error": "Invalid organization_id"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            corporates = Corporateentity.objects.all()

        serializer = AllCorporateListSerializer(corporates, many=True)
        return Response(serializer.data)