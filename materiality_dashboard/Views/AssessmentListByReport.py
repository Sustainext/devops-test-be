from materiality_dashboard.models import MaterialityAssessment
from materiality_dashboard.Serializers.MaterialityAssessmentSerializer import (
    MaterialityAssessmentSerializer,
)
from rest_framework.response import Response
from rest_framework.views import APIView


class GetAssessmentListForReport(APIView):
    def get(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        organization_id = request.query_params.get("organization_id")
        corporate_id = request.query_params.get("corporate_id")
        report_type = request.query_params.get("report_type")
        report_by = request.query_params.get("report_by")
        try:
            if report_by == "Organization":
                materiality_assessments = MaterialityAssessment.objects.filter(
                    client_id=request.user.client.id,
                    start_date__gte=start_date,
                    end_date__lte=end_date,
                    organization_id=organization_id,
                    corporate_id__isnull=True,
                    approach=report_type,
                )
            else:
                if corporate_id:
                    materiality_assessments = MaterialityAssessment.objects.filter(
                        client_id=request.user.client.id,
                        start_date__gte=start_date,
                        end_date__lte=end_date,
                        organization_id=organization_id,
                        corporate_id=corporate_id,
                        approach=report_type,
                    )
                else:
                    return Response({"message": "corporate_id is required"}, status=200)
            serializer = MaterialityAssessmentSerializer(
                materiality_assessments, many=True
            )
            data = serializer.data
            if len(data) > 1:
                return Response(data)
            return Response([])
        except MaterialityAssessment.DoesNotExist:
            return Response({"message": "Materiality assessment not found"}, status=404)
