from materiality_dashboard.models import MaterialityAssessment
from materiality_dashboard.Serializers.MaterialityAssessmentSerializer import (
    MaterialityAssessmentSerializer,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


class GetAssessmentListForReport(APIView):
    def get(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        organization_id = request.query_params.get("organization_id")
        corporate_id = request.query_params.get("corporate_id")
        report_by = request.query_params.get("report_by")
        approach = request.query_params.get("approach")

        if not all([start_date, end_date, organization_id, report_by, approach]):
            return Response(
                {"message": "Please provide start_date, end_date, organization_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            if report_by == "Organization":
                materiality_assessments = MaterialityAssessment.objects.filter(
                    client_id=request.user.client.id,
                    start_date__gte=start_date,
                    end_date__lte=end_date,
                    organization_id=organization_id,
                    corporate_id__isnull=True,
                    approach__icontains=approach,
                )
            else:
                if corporate_id:
                    materiality_assessments = MaterialityAssessment.objects.filter(
                        client_id=request.user.client.id,
                        start_date__gte=start_date,
                        end_date__lte=end_date,
                        organization_id=organization_id,
                        corporate_id=corporate_id,
                        approach__icontains=approach,
                    )
                elif report_by == "Corporate" and corporate_id is None:
                    return Response({"message": "corporate_id is required"}, status=200)
                else:
                    return Response([])
            serializer = MaterialityAssessmentSerializer(
                materiality_assessments, many=True
            )

            return Response(serializer.data)
        except MaterialityAssessment.DoesNotExist:
            return Response({"message": "Materiality assessment not found"}, status=404)
