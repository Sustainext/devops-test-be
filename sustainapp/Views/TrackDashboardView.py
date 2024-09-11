from sustainapp.models import TrackDashboard
from sustainapp.Serializers.TrackDashboardSerializer import TrackDashboardSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class TrackDashboardAPIView(APIView):
    def get(self, request):
        trackdashboard = TrackDashboard.objects.filter(client_id=request.user.client_id)
        print(trackdashboard)
        serializer = TrackDashboardSerializer(trackdashboard, many=True)
        return Response(serializer.data)
