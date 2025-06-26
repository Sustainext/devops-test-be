from weasyprint import HTML
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from sustainapp.models import Report
from django.shortcuts import get_object_or_404
from apps.tcfd_framework.report.services.GetTCFDReportData import GetTCFDReportData
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from apps.tcfd_framework.report.models import TCFDReport
from apps.tcfd_framework.report.serializers import TCFDReportSerializer


class GetTCFDReportPdf(View):
    def get_report_data(self, screen_name, report_id):
        try:
            tcfd_report = TCFDReport.objects.get(
                report_id=report_id, screen_name=screen_name
            )
        except TCFDReport.DoesNotExist:
            return []

        serializer = TCFDReportSerializer(tcfd_report)
        report_data = serializer.data["data"]
        return report_data

    def get(self, request, *args, **kwargs):
        report_id = kwargs.get("report_id")
        report = get_object_or_404(Report, id=report_id)
        try:
            collect_data_object = GetTCFDReportData(report=report)
        except ValidationError:
            return Response(
                data={"message": "Invalid report id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        screen_name_list = [
            "message_ceo",
            "about_report",
            "about_company",
            "governance",
            "strategy",
            "risk_management",
            "metrics_targets",
            "tcfd_content_index",
            "annexure",
        ]
        all_screen_data = {}
        for screen_name in screen_name_list:
            data = collect_data_object.get_data_as_per_screen(screen_name)
            if not isinstance(data, dict):
                data = {"records": data}
            if screen_name != "tcfd_content_index":
                data["report_data"] = self.get_report_data(screen_name, report_id)
            all_screen_data[screen_name] = data

        context = {
            "report": report,
            **{
                f"screen_{number}": all_screen_data[screen_name]
                for number, screen_name in enumerate(screen_name_list, start=1)
            },
        }

        template = get_template("TCFD.html")
        final_html_content = template.render(context, request)

        response = HttpResponse(content_type="application/pdf")
        disposition = "attachment" if "download" in request.GET else "inline"
        response["Content-Disposition"] = f'{disposition}; filename="TCFD-report.pdf"'
        HTML(string=final_html_content).write_pdf(response)

        return response
