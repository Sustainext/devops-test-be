from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.views import View
from sustainapp.models import Report
import time
from weasyprint import HTML
from xhtml2pdf import pisa
from esg_report.services.screen_one_service import CeoMessageService
from esg_report.services.screen_two_service import ScreenTwoService
from esg_report.services.screen_three_service import MissionVisionValuesService
from esg_report.services.screen_four_service import SustainabilityRoadmapService
from esg_report.services.screen_five_service import AwardsAndRecognitionService
from esg_report.services.screen_six_service import StakeholderEngagementService
from esg_report.services.screen_seven_service import AboutTheReportService
from esg_report.services.screen_eight_service import MaterialityService
from esg_report.services.screen_nine_service import ScreenNineService
from esg_report.services.screen_ten_service import ScreenTenService
from esg_report.services.screen_eleven_service import ScreenElevenService
from esg_report.services.screen_twelve_service import ScreenTwelveService
from esg_report.services.screen_thirteen_service import ScreenThirteenService
from esg_report.services.screen_fourteen_service import ScreenFourteenService
from esg_report.services.screen_fifteen_service import ScreenFifteenService
from django.forms import model_to_dict
from authentication.models import CustomUser
from esg_report.services.data import context_data
import json
from threading import Thread


def convert_keys(obj):
    if isinstance(obj, dict):
        new_obj = {}
        for key, value in obj.items():
            # Replace '-' with '_'
            new_key = key.replace("-", "_")
            # Recursively call convert_keys on the value if it's a dict or list
            new_obj[new_key] = convert_keys(value)
        return new_obj
    elif isinstance(obj, list):
        return [convert_keys(item) for item in obj]
    else:
        return obj


class ESGReportPDFView(View):
    def get(self, request, *args, **kwargs):
        start_time = time.time()
        user = request.user
        pk = self.kwargs.get("pk")
        results = {}

        # Function to retrieve report
        def fetch_report():
            try:
                results["report"] = CeoMessageService.get_report_by_id(pk)
            except Report.DoesNotExist:
                results["error"] = HttpResponse(
                    f"No report found with ID={pk}", status=404
                )
            except Exception as e:
                results["error"] = HttpResponse(
                    "An unexpected error occurred while retrieving the report.",
                    status=500,
                )

        def get_ceo_message():
            ceo_message = CeoMessageService.get_ceo_message_by_report(results["report"])
            dict_ceo_message = model_to_dict(ceo_message) if ceo_message else {}
            results["ceo_message"] = convert_keys(dict_ceo_message)

        def get_about_the_company():
            service = ScreenTwoService(user)
            about_the_company_service, is_new = service.fetch_about_company(
                results["report"]
            )
            about_the_company = service.get_about_company_data(
                about_the_company_service, results["report"], request
            )
            results["about_the_company"] = convert_keys(about_the_company)

        def get_mission_vision_values():
            mission_vision_values = (
                MissionVisionValuesService.get_mission_vision_values_by_report_id(pk)
            )
            results["mission_vision_values"] = convert_keys(mission_vision_values)

        def get_sustainability_roadmap():
            sustainability_roadmap = (
                SustainabilityRoadmapService.get_sustainability_roadmap_by_report_id(pk)
            )
            results["sustainability_roadmap"] = convert_keys(sustainability_roadmap)

        def get_awards_and_recognition():
            awards_and_recognition = (
                AwardsAndRecognitionService.get_awards_and_recognition_by_report_id(pk)
            )
            results["awards_and_recognition"] = convert_keys(awards_and_recognition)

        def get_stakeholder_engagement():
            stakeholder_engagement = (
                StakeholderEngagementService.get_stakeholder_engagement_by_report_id(
                    pk, user
                )
            )
            results["stakeholder_engagement"] = convert_keys(stakeholder_engagement)

        def get_about_the_report():
            about_the_report = AboutTheReportService.get_about_the_report_data(pk, user)
            results["about_the_report"] = convert_keys(about_the_report)

        def get_materiality():
            materiality = MaterialityService.get_materiality_data(pk)
            results["materiality"] = convert_keys(materiality)

        def get_screen_nine_data():
            screen_nine_service = ScreenNineService(report_id=pk)
            results["screen_nine_data"] = screen_nine_service.get_response()

        def get_screen_ten_data():
            screen_ten_data = ScreenTenService.get_screen_ten(pk)
            results["screen_ten_data"] = convert_keys(screen_ten_data)

        def get_screen_eleven_data():
            screen_eleven_service = ScreenElevenService(report_id=pk, request=request)
            results["screen_eleven_data"] = screen_eleven_service.get_report_response()

        def get_screen_twelve_data():
            screen_twelve_service = ScreenTwelveService(report_id=pk, request=request)
            results["screen_twelve_data"] = convert_keys(
                screen_twelve_service.get_report_response()
            )

        def get_screen_thirteen_data():
            screen_thirteen_service = ScreenThirteenService(
                report_id=pk, request=request
            )
            results["screen_thirteen_data"] = convert_keys(
                screen_thirteen_service.get_report_response()
            )

        def get_screen_fourteen_data():
            screen_fourteen_service = ScreenFourteenService(
                report_id=pk, request=request
            )
            results["screen_fourteen_data"] = convert_keys(
                screen_fourteen_service.get_report_response()
            )

        def get_screen_fifteen_data():
            screen_fifteen_service = ScreenFifteenService(report_id=pk, request=request)
            results["screen_fifteen_data"] = convert_keys(
                screen_fifteen_service.get_report_response()
            )

        fetch_report()
        # List of threads to run
        threads = [
            Thread(target=get_ceo_message),
            Thread(target=get_about_the_company),
            Thread(target=get_mission_vision_values),
            Thread(target=get_sustainability_roadmap),
            Thread(target=get_awards_and_recognition),
            Thread(target=get_stakeholder_engagement),
            Thread(target=get_about_the_report),
            Thread(target=get_materiality),
            Thread(target=get_screen_nine_data),
            Thread(target=get_screen_ten_data),
            Thread(target=get_screen_eleven_data),
            Thread(target=get_screen_twelve_data),
            Thread(target=get_screen_thirteen_data),
            Thread(target=get_screen_fourteen_data),
            Thread(target=get_screen_fifteen_data),
        ]

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Handle errors from fetching report
        if "error" in results:
            return results["error"]

        # Create context for rendering
        context = {
            "report": results["report"],
            "ceo_message": results["ceo_message"],
            "about_the_company": results["about_the_company"],
            "mission_vision_values": results["mission_vision_values"],
            "sustainability_roadmap": results["sustainability_roadmap"],
            "awards_and_recognition": results["awards_and_recognition"],
            "stakeholder_engagement": results["stakeholder_engagement"],
            "about_the_report": results["about_the_report"],
            "materiality": results["materiality"],
            "screen_nine_data": results["screen_nine_data"],
            "screen_ten_data": results["screen_ten_data"],
            "screen_eleven_data": results["screen_eleven_data"],
            "screen_twelve_data": results["screen_twelve_data"],
            "screen_thirteen_data": results["screen_thirteen_data"],
            "screen_fourteen_data": results["screen_fourteen_data"],
            "screen_fifteen_data": results["screen_fifteen_data"],
            "pk": pk,
        }

        template_path = "esg_report.html"
        try:
            # Get the template and render HTML
            template = get_template(template_path)
            html_content = template.render(context, request)
        except Exception as e:
            print(f"Error rendering the PDF template: {e}")
            return HttpResponse("Error rendering the PDF template.", status=500)

        # Configure the response to return a PDF file
        response = HttpResponse(content_type="application/pdf")
        disposition = "attachment" if "download" in request.GET else "inline"
        pdf_filename = f"{results['report'].name}.pdf"
        response["Content-Disposition"] = f'{disposition}; filename="{pdf_filename}"'

        try:
            # Generate the PDF with WeasyPrint
            HTML(string=html_content).write_pdf(response)

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
