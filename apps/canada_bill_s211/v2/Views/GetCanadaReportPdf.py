from weasyprint import HTML
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from sustainapp.models import Report
from apps.canada_bill_s211.v2.services.bill_s211_data import BillS211ScreenDataService
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError


class GetCanadaReportPdf(View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs.get("report_id")
        report = get_object_or_404(Report, id=report_id)
        all_screen_data = {}
        for screen_number in range(1, 13):
            try:
                service = BillS211ScreenDataService(report, screen=screen_number)
                screen_data = service.get_screen_wise_data()
                all_screen_data[f"screen_{screen_number}"] = screen_data
            except ValidationError as e:
                all_screen_data[f"screen_{screen_number}"] = {"error": str(e)}

        context = {
            "report": report,
            "screen_1": all_screen_data.get("screen_1", {}),
            "screen_2": all_screen_data.get("screen_2", {}),
            "screen_3": all_screen_data.get("screen_3", {}),
            "screen_4": all_screen_data.get("screen_4", {}),
            "screen_5": all_screen_data.get("screen_5", {}),
            "screen_6": all_screen_data.get("screen_6", {}),
            "screen_7": all_screen_data.get("screen_7", {}),
            "screen_8": all_screen_data.get("screen_8", {}),
            "screen_9": all_screen_data.get("screen_9", {}),
            "screen_10": all_screen_data.get("screen_10", {}),
            "screen_11": all_screen_data.get("screen_11", {}),
            "screen_12": all_screen_data.get("screen_12", {}),
        }
        template = get_template("canada_bills211.html")
        html_content = template.render(context, request)
        # Configure the response to return a PDF file
        response = HttpResponse(content_type="application/pdf")
        disposition = "attachment" if "download" in request.GET else "inline"
        pdf_filename = "sample.pdf"
        response["Content-Disposition"] = f'{disposition}; filename="{pdf_filename}"'

        # Generate the PDF with WeasyPrint
        HTML(string=html_content).write_pdf(response)

        return response
