from rest_framework.generics import ListAPIView
from materiality_dashboard.models import StakeholderEngagement
from materiality_dashboard.Serializers.StockholderEngagementSerializer import (
    StakeholderEngagementSerializer,
)
from rest_framework.permissions import IsAuthenticated


class StakeholderEngagementListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = StakeholderEngagement.objects.all()
    serializer_class = StakeholderEngagementSerializer
