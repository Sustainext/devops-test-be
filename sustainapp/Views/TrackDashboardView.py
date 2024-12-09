from sustainapp.models import TrackDashboard
from sustainapp.Serializers.TrackDashboardSerializer import TrackDashboardSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

class TrackDashboardAPIView(APIView):
    def get(self, request):
        trackdashboard = TrackDashboard.objects.all()
        serializer = TrackDashboardSerializer(trackdashboard, many=True)
        return Response(serializer.data)
