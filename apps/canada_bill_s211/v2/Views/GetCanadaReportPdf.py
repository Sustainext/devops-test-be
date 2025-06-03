from weasyprint import HTML
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from sustainapp.models import Report


class GetCanadaReportPdf(View):
    def get(self, request, *args, **kwargs):
        # Get the report ID from the URL
        report_id = kwargs.get("report_id")
        # Fetch the report data from the database
        report = Report.objects.get(id=report_id)
        # Render the HTML template with the report data
        context = {
            "report": report,
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
