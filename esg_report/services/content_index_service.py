# services.py
from esg_report.models.StatementOfUse import StatementOfUseModel
from esg_report.Serializer.StatementOfUseSerializer import StatementOfUseSerializer
from rest_framework.exceptions import NotFound
from sustainapp.models import Report


class StatementOfUseService:
    @staticmethod
    def get_statement_of_use(report_id: int):
        # Fetch the report
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            raise NotFound(detail="Report not found")

        # Fetch the statement of use for the given report
        try:
            statement_of_use = StatementOfUseModel.objects.get(report=report)
            return StatementOfUseSerializer(statement_of_use).data
        except StatementOfUseModel.DoesNotExist:
            return {
                "report": report_id,
                "statement_of_use": "",
            }
