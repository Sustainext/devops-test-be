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
    ContentIndexUpdateSerializer,
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
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response({"error": "Report not found"}, status=404)

        serializer = ContentIndexUpdateSerializer(data={"sections": request.data})
        serializer.is_valid(raise_exception=True)

        all_items = []

        for section in serializer.validated_data["sections"]:
            if section.get("items"):
                all_items.extend(section["items"])
            if section.get("sections"):
                for heading2 in section["sections"]:
                    for heading3 in heading2["sections"]:
                        all_items.extend(heading3["items"])

        for item in all_items:
            omission_data = item.get("omission", [{}])[0]
            reason = omission_data.get("reason")
            explanation = omission_data.get("explanation")

            # Determine is_filled based on provided value
            is_filled = item.get("is_filled", False)

            # Apply condition:
            # If is_filled is True → req_omitted = None
            # If is_filled is False → req_omitted = item["key"]
            omission_data["req_omitted"] = None if is_filled else item["key"]

            # Save to DB
            ContentIndexRequirementOmissionReason.objects.update_or_create(
                report=report,
                indicator=item["key"],
                defaults={
                    "reason": reason,
                    "explanation": explanation,
                    "is_filled": is_filled ,
                },
            )

        return Response({"message": "Content Index updated successfully."}, status=status.HTTP_200_OK)
   
    

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
    Only includes disclosures where all required data points are filled.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id: int, format=None):

        def flatten_disclosure_structure(data):
            output = []
            for section in data:
                for item in section:  # Flatten the nested list
                    if item.get("items"):  # Only add non-empty item groups
                        output.append(item)
            return [output] if output else []

        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response({"error": "Report not found"}, status=404)

        output = [
            generate_disclosure_status_reference(
                report, GENERAL_DISCLOSURES_AND_PATHS, "General Disclosures", is_material=False, filter_filled=True
            ),
            generate_disclosure_status_reference(
                report, MATERIAL_TOPICS_AND_PATHS, "Material Topics", is_material=True, filter_filled=True
            ),
        ]

        final_output = flatten_disclosure_structure(output)

        # Optional: Ensure each item group also has data
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


