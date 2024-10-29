from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.views import View
from sustainapp.models import Report
import time
from xhtml2pdf import pisa
from esg_report.services.screen_one_service import CeoMessageService
from esg_report.services.screen_two_service import AboutTheCompanyAndOperationsService
from esg_report.services.screen_three_service import MissionVisionValuesService
from esg_report.services.screen_four_service import SustainabilityRoadmapService
from esg_report.services.screen_five_service import AwardsAndRecognitionService
from esg_report.services.screen_six_service import StakeholderEngagementService
from esg_report.services.screen_seven_service import AboutTheReportService
from esg_report.services.screen_eight_service import MaterialityService
from esg_report.services.screen_ten_service import ScreenTenService
from django.forms import model_to_dict
from authentication.models import CustomUser


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
        user = CustomUser.objects.get(id=1)

        pk = self.kwargs.get("pk")
        try:
            # Retrieve the report object
            report = CeoMessageService.get_report_by_id(pk)
        except Report.DoesNotExist:
            return HttpResponse(f"No report found with ID={pk}", status=404)
        except Exception as e:
            return HttpResponse(
                "An unexpected error occurred while retrieving the report.", status=500
            )
        # ceo_message = CeoMessageService.get_ceo_message_by_report(report)
        # dict_ceo_message = model_to_dict(ceo_message)
        # dict_ceo_message = convert_keys(dict_ceo_message)
        # about_the_company_service = AboutTheCompanyAndOperationsService(pk, user)
        # about_the_company = about_the_company_service.get_complete_report_data()
        # about_the_company = convert_keys(about_the_company)
        # mission_vision_values = (
        #     MissionVisionValuesService.get_mission_vision_values_by_report_id(pk)
        # )
        # mission_vision_values = convert_keys(mission_vision_values)
        # sustainability_roadmap = (
        #     SustainabilityRoadmapService.get_sustainability_roadmap_by_report_id(pk)
        # )
        # sustainability_roadmap = convert_keys(sustainability_roadmap)
        # awards_and_recognition = (
        #     AwardsAndRecognitionService.get_awards_and_recognition_by_report_id(pk)
        # )
        # awards_and_recognition = convert_keys(awards_and_recognition)
        # stakeholder_engagement = (
        #     StakeholderEngagementService.get_stakeholder_engagement_by_report_id(
        #         pk, user
        #     )
        # )
        # stakeholder_engagement = convert_keys(stakeholder_engagement)
        # about_the_report = AboutTheReportService.get_about_the_report_data(pk, user)
        # about_the_report = convert_keys(about_the_report)
        # materiality = MaterialityService.get_materiality_data(pk)
        # materiality = convert_keys(materiality)
        # screen_nine_data = ScreenNineService.get_screen_nine_data(pk)
        screen_ten_data = ScreenTenService.get_screen_ten(pk)
        screen_ten_data = convert_keys(screen_ten_data)
        print(screen_ten_data)
        # Prepare the context for rendering the PDF template
        context = {
            "report": report,
            # "ceo_message": dict_ceo_message,
            # "about_the_company": about_the_company,
            # "mission_vision_values": mission_vision_values,
            # "sustainability_roadmap": sustainability_roadmap,
            # "awards_and_recognition": awards_and_recognition,
            # "stakeholder_engagement": stakeholder_engagement,
            # "about_the_report": about_the_report,
            # "materiality": materiality,
            # "screen_nine_data": screen_nine_data,
            "screen_ten_data": screen_ten_data,
            "pk": pk,
        }

        template_path = "esg_report.html"
        try:
            # Get the template and render HTML
            template = get_template(template_path)
            html = template.render(context, request)
        except Exception as e:
            print(f"Error rendering the PDF template: {e}")
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
            return HttpResponse(
                "Unexpected error occurred while generating the PDF.", status=500
            )
