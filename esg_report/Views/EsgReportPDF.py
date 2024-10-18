from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.views import View
from sustainapp.models import Report
from django.conf import settings
import time
from xhtml2pdf import pisa


class ESGReportPDFView(View):
    def get(self, request, *args, **kwargs):
        start_time = time.time()

        pk = self.kwargs.get("pk")
        try:
            # Retrieve the report object
            report = get_object_or_404(Report, pk=pk)
        except Report.DoesNotExist:
            return HttpResponse(f"No report found with ID={pk}", status=404)
        except Exception as e:
            print(f"Error retrieving report: {e}")
            return HttpResponse(
                "An unexpected error occurred while retrieving the report.", status=500
            )

        # Prepare the context for rendering the PDF template
        context = {
            "report": report,
            "pk": pk,
        }

        template_path = "esg_report.html"
        try:
            # Get the template and render HTML
            template = get_template(template_path)
            html = template.render(context, request)
        except Exception as e:
            print(f"Error rendering template: {e}")
            return HttpResponse("Error rendering the PDF template.", status=500)

        response = HttpResponse(content_type="application/pdf")
        try:
            # Check if the PDF should be downloaded or viewed inline
            disposition = "attachment" if "download" in request.GET else "inline"
            pdf_filename = (
                f"{report.name}.pdf"  # Assuming `name` is a field in the `Report` model
            )
            response["Content-Disposition"] = (
                f'{disposition}; filename="{pdf_filename}"'
            )

            # Generate the PDF
            pisa_status = pisa.CreatePDF(html, dest=response)
            if pisa_status.err:
                return HttpResponse("Error generating PDF", status=500)

            # Print time taken for PDF generation
            print(
                f"Total time taken to generate PDF: {time.time() - start_time:.2f} seconds."
            )
            return response

        except Exception as e:
            print(f"Error generating PDF: {e}")
            return HttpResponse(
                "Unexpected error occurred while generating the PDF.", status=500
            )
