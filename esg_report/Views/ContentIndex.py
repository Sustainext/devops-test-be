from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from materiality_dashboard.models import (
    MaterialityAssessment,
    MaterialTopic,
    Disclosure,
)
from esg_report.models.StatementOfUse import StatementOfUseModel
from esg_report.models.ContentIndexRequirementOmissionReason import (
    ContentIndexRequirementOmissionReason,
)
from esg_report.Serializer.ContentIndexRequirementOmissionReasonsSerializer import (
    ContentIndexRequirementOmissionReasonsSerializer,
)
from esg_report.Serializer.StatementOfUseSerializer import StatementOfUseSerializer
from esg_report.Serializer.ContentIndexDataValidationSerializer import (
    DataListSerializer,
)
from datametric.models import Path
from sustainapp.models import Report
from esg_report.utils import generate_disclosure_status,generate_disclosure_status_reference
from common.enums.GeneralTopicDisclosuresAndPaths import GENERAL_DISCLOSURES_AND_PATHS
from common.enums.ManagementMatearilTopicsAndPaths import MATERIAL_TOPICS_AND_PATHS


class GetContentIndex(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id: int, format=None):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response({"error": "Report not found"}, status=404)

        output = [
            generate_disclosure_status(report, GENERAL_DISCLOSURES_AND_PATHS, "General Disclosures", is_material=False),
            generate_disclosure_status(report, MATERIAL_TOPICS_AND_PATHS, "Material Topics", is_material=True),
        ]
        return Response(output, status=200)
    

    def put(self, request, report_id: int, format=None):
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = DataListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        for data in serializer.validated_data["items"]:
            content_index_omission_reason, _ = (
                ContentIndexRequirementOmissionReason.objects.update_or_create(
                    report=self.report,
                    indicator=data["key"],
                    defaults={
                        "reason": data["omission"][0]["reason"],
                        "explanation": data["omission"][0]["explanation"],
                        "is_filled": data["is_filled"],
                    },
                )
            )
            content_index_omission_reason.save()
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class GetContentIndexReferenec(APIView):
    """
    Retrieve and return a filtered list of filled GRI disclosures for a given report.

    This endpoint combines both General Disclosures and Material Topics, but only includes 
    disclosure items where all required data points are filled. It also removes omission 
    details from the response and flattens the nested structure into a single grouped list.

    Args:
        request (HttpRequest): The incoming HTTP request.
        report_id (int): The primary key of the report instance.
        format (str, optional): Optional format specifier.

    Returns:
        Response: A JSON-formatted response containing a list with a single element (list), 
                  where each element is a grouped dictionary with:
                  - 'heading1': section title (e.g., "General Disclosures", or a GRI subheading)
                  - 'items': list of filled disclosures for that section
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id: int, format=None):

        def flatten_disclosure_structure(data):
            output = []
            for section in data:
                for item in section:  # Flatten the nested list
                    output.append(item)
            return [output]
        
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response({"error": "Report not found"}, status=404)
    
        output = [
            generate_disclosure_status_reference(report, GENERAL_DISCLOSURES_AND_PATHS, "General Disclosures", is_material=False),
            generate_disclosure_status_reference(report, MATERIAL_TOPICS_AND_PATHS, "Material Topics", is_material=True),
        ]

        final_output = flatten_disclosure_structure(output)
        return Response(final_output, status=200)



class StatementOfUseAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id: int, format=None):
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            self.statement_of_use = StatementOfUseModel.objects.get(report=self.report)
        except StatementOfUseModel.DoesNotExist:
            return Response(
                {
                    "report": report_id,
                    "statement_of_use": "",
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            StatementOfUseSerializer(self.statement_of_use).data,
            status=status.HTTP_200_OK,
        )

    def put(self, request, report_id: int, format=None):
        try:
            self.report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            self.statement_of_use = StatementOfUseModel.objects.get(report=self.report)
            serializer = StatementOfUseSerializer(
                self.statement_of_use, data=request.data
            )
        except StatementOfUseModel.DoesNotExist:
            serializer = StatementOfUseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(report=self.report)
        return Response(serializer.data, status=status.HTTP_200_OK)
