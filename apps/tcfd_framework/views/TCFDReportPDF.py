from weasyprint import HTML
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from sustainapp.models import Report
from django.shortcuts import get_object_or_404


class GetTCFDReportPdf(View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs.get("report_id")
        report = get_object_or_404(Report, id=report_id)

        context = {"report": report}
        template = get_template("TCFD.html")
        final_html_content = template.render(context, request)

        response = HttpResponse(content_type="application/pdf")
        disposition = "attachment" if "download" in request.GET else "inline"
        response["Content-Disposition"] = f'{disposition}; filename="TCFD-report.pdf"'
        HTML(string=final_html_content).write_pdf(response)

        return response
