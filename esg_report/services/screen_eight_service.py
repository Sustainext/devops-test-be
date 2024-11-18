from esg_report.models.ScreenEight import MaterialityStatement
from esg_report.Serializer.MaterialityStatementSerializer import (
    MaterialityStatementSerializer,
)
from sustainapp.models import Report
from esg_report.utils import get_materiality_assessment
from materiality_dashboard.models import MaterialityAssessment
from materiality_dashboard.Serializers.MaterialityImpactSerializer import (
    MaterialityImpactSerializer,
)
from django.core.exceptions import ObjectDoesNotExist


class MaterialityService:
    @staticmethod
    def get_materiality_data(report_id, request=None):
        response_data = {}

        # Fetch the report
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            raise ObjectDoesNotExist("Report not found")

        # Retrieve Materiality Statement
        try:
            materiality_statement: MaterialityStatement = report.materiality_statement
            serializer = MaterialityStatementSerializer(
                materiality_statement, context={"request": request}
            )
            response_data.update(serializer.data)
        except ObjectDoesNotExist:
            response_data["statement"] = None

        # Retrieve Materiality Assessment
        materiality_assessment = get_materiality_assessment(report)
        response_data["materiality_topics"] = {}

        # 3-2b: Reason for Change
        try:
            response_data["3-2b"] = (
                materiality_assessment.change_confirmation.reason_for_change
            )
        except (ObjectDoesNotExist, AttributeError):
            response_data["3-2b"] = None

        # 3-1-a: Assessment Process
        try:
            assessment_process = materiality_assessment.assessment_process.all().get()
            response_data["3-1-a"] = {
                "process_description": assessment_process.process_description,
                "impact_assessment_process": assessment_process.impact_assessment_process,
                "selected_stakeholders": list(
                    assessment_process.selected_stakeholders.all().values_list(
                        "name", flat=True
                    )
                ),
            }
        except (ObjectDoesNotExist, AttributeError):
            response_data["3-1-a"] = None

        # 3-3a: Management Impacts
        try:
            response_data["3-3a"] = MaterialityImpactSerializer(
                materiality_assessment.management_impacts.all(), many=True
            ).data
        except (ObjectDoesNotExist, AttributeError):
            response_data["3-3a"] = None

        # 3-3b: Negative Impact Involvement Description
        try:
            response_data["3-3b"] = (
                materiality_assessment.management_approach_questions.all()
                .get()
                .negative_impact_involvement_description
            )
        except (ObjectDoesNotExist, AttributeError):
            response_data["3-3b"] = None

        return response_data
