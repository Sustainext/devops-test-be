from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from sustainapp.models import Report, Location
import time
from weasyprint import HTML
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

# from esg_report.services.content_index_service import StatementOfUseService
from django.forms import model_to_dict
from threading import Thread
from common.enums.GeneralTopicDisclosuresAndPaths import GENERAL_DISCLOSURES_AND_PATHS
from common.enums.ManagementMatearilTopicsAndPaths import MATERIAL_TOPICS_AND_PATHS
from esg_report.utils import generate_disclosure_status,generate_disclosure_status_reference



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


def process_benefits(benefits_key, screen_thirteen_data, location_name_map):
    """
    Processes benefits for a specific key (e.g., full-time, part-time, temporary employees).
    Enriches the data with location names based on the selectedLocations.
    """
    if screen_thirteen_data.get("401_social_analyse") is not None:
        benefits = (
            screen_thirteen_data.get("401_social_analyse", {})
            .get("data", {})
            .get("benefits", {})
            .get(benefits_key, [])
        )
    else:
        benefits = []

    for benefit in benefits:
        benefit["selectedLocations_name"] = [
            location_name_map.get(loc_id, f"Unknown ID: {loc_id}")
            for loc_id in benefit.get("selectedLocations", [])
        ]
    return benefits


class ESGReportPDFView(View):
    def preprocess_esg_data(self, data):
        if not data:
            return {}
        processed_rows = []

        for esg_category, topics in data.items():
            # Calculate ESG row span: Sum of all disclosures under the ESG category
            esg_rowspan = sum(
                len(
                    [
                        disclosure
                        for disclosure in topic["disclosure"]
                        if disclosure["show_on_table"]
                    ]
                )
                for topic in topics
            )

            for topic in topics:
                # Calculate Material Topic row span: Count disclosures under the topic that should be shown
                topic_rowspan = len(
                    [
                        disclosure
                        for disclosure in topic["disclosure"]
                        if disclosure["show_on_table"]
                    ]
                )

                for disclosure in topic["disclosure"]:
                    if disclosure["show_on_table"]:
                        # Add the row data
                        processed_rows.append(
                            {
                                "esg_category": esg_category.capitalize(),
                                "esg_rowspan": esg_rowspan
                                if len(processed_rows) == 0
                                or processed_rows[-1]["esg_category"]
                                != esg_category.capitalize()
                                else 0,  # Only once per ESG category
                                "material_topic": topic["name"],
                                "topic_rowspan": topic_rowspan
                                if len(processed_rows) == 0
                                or processed_rows[-1]["material_topic"] != topic["name"]
                                else 0,  # Only once per Material Topic
                                "gri_disclosure_number": disclosure["name"],
                                "linked_sdg": disclosure.get("relevent_sdg", None),
                            }
                        )
        return processed_rows

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
            except Exception:
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

            about_the_company = service.get_screen_two_data(pk, request)

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
            # TODO: Implement raw_responses logic in this method, should be same as ScreenTwo API View.
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
            screen_thirteen_data = screen_thirteen_service.get_report_response()

            # Extract all unique location IDs from selectedLocations for all benefit types
            all_location_ids = set()

            benefit_types = [
                "benefits_full_time_employees",
                "benefits_part_time_employees",
                "benefits_temporary_employees",
            ]

            for benefit_type in benefit_types:
                if screen_thirteen_data.get("401_social_analyse") is not None:
                    benefits = (
                        screen_thirteen_data.get("401_social_analyse", {})
                        .get("data", {})
                        .get("benefits", {})
                        .get(benefit_type, [])
                    )
                else:
                    benefits = []
                for benefit in benefits:
                    all_location_ids.update(benefit.get("selectedLocations", []))

            # Fetch location names from the database
            location_names = Location.objects.filter(id__in=all_location_ids).values(
                "id", "name"
            )
            location_name_map = {loc["id"]: loc["name"] for loc in location_names}

            # Process each category of benefits
            process_benefits(
                "benefits_full_time_employees", screen_thirteen_data, location_name_map
            )
            process_benefits(
                "benefits_part_time_employees", screen_thirteen_data, location_name_map
            )
            process_benefits(
                "benefits_temporary_employees", screen_thirteen_data, location_name_map
            )

            # Update the results dictionary
            results["screen_thirteen_data"] = convert_keys(screen_thirteen_data)

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
        content_index_only = request.GET.get("content_index", "false").lower() == "true"

        if content_index_only:
            # Generate content index data only
            content_index_data = [
                generate_disclosure_status(report=results["report"], topic_mapping=GENERAL_DISCLOSURES_AND_PATHS, heading="General Disclosures", is_material=False),
                generate_disclosure_status(report=results["report"], topic_mapping=MATERIAL_TOPICS_AND_PATHS, heading="Material Topics", is_material=True),
            ]
           
            # statement_of_use = StatementOfUseService.get_statement_of_use(report_id=pk)

            # Prepare context for content index only
            context = {
                "report": results["report"],
                "content_index_only": content_index_only,
                "content_index_data": content_index_data,
                "pk": pk,  # Pass the report ID to the template
            }
            template_path = "content_index/esg_content_index.html"  # Use a dedicated template or adapt the existing one
            try:
                template = get_template(template_path)
                html_content = template.render(context, request)
            except Exception as e:
                print(f"Error rendering the PDF template: {e}")
                return HttpResponse("Error rendering the PDF template.", status=500)

            # Configure the response for PDF output
            response = HttpResponse(content_type="application/pdf")
            disposition = "attachment" if "download" in request.GET else "inline"
            pdf_filename = f"{results['report'].name}_content_index.pdf"
            response["Content-Disposition"] = (
                f'{disposition}; filename="{pdf_filename}"'
            )

            try:
                # Generate the PDF with WeasyPrint
                HTML(string=html_content).write_pdf(response)

                # Print time taken for PDF generation
                print(
                    f"Total time taken to generate content index PDF: {time.time() - start_time:.2f} seconds."
                )
                return response

            except Exception as e:
                print(f"Error generating content index PDF: {e}")
                return HttpResponse(
                    "Unexpected error occurred while generating the PDF.", status=500
                )
            
        if results["report"].report_type == "GRI Report: In accordance With":
            content_index_data = {
                "report_type": results["report"].report_type,
                "sections":[
                                generate_disclosure_status(
                                    report=results["report"],
                                    topic_mapping=GENERAL_DISCLOSURES_AND_PATHS,
                                    heading="General Disclosures",
                                    is_material=False,
                                ),
                                generate_disclosure_status(
                                    report=results["report"],
                                    topic_mapping=MATERIAL_TOPICS_AND_PATHS,
                                    heading="Material Topics",
                                    is_material=True,
                                ),
                            ]
                        }
            
        elif results["report"].report_type == "GRI Report: With Reference to":
            content_index_data = {
                 "report_type": results["report"].report_type,
                  "sections":[
                            generate_disclosure_status_reference(
                                results["report"],
                                GENERAL_DISCLOSURES_AND_PATHS,
                                "General Disclosures",
                                is_material=False,
                                filter_filled=True,
                            ),
                            generate_disclosure_status_reference(
                                results["report"],
                                MATERIAL_TOPICS_AND_PATHS,
                                "Material Topics",
                                is_material=True,
                                filter_filled=True,
                            ),
                        ]
            }
            
        else:
            content_index_data = []
        

        # statement_of_use = StatementOfUseService.get_statement_of_use(report_id=pk)
        materiality_table_data = self.preprocess_esg_data(
            results["materiality"]["8_1_1"]
        )
        # Create context for rendering
        context = {
            "report": results["report"] if "report" in results else None,
            "ceo_message": results["ceo_message"] if "ceo_message" in results else None,
            "about_the_company": (
                results["about_the_company"] if "about_the_company" in results else None
            ),
            "mission_vision_values": (
                results["mission_vision_values"]
                if "mission_vision_values" in results
                else None
            ),
            "sustainability_roadmap": (
                results["sustainability_roadmap"]
                if "sustainability_roadmap" in results
                else None
            ),
            "awards_and_recognition": (
                results["awards_and_recognition"]
                if "awards_and_recognition" in results
                else None
            ),
            "stakeholder_engagement": (
                results["stakeholder_engagement"]
                if "stakeholder_engagement" in results
                else None
            ),
            "about_the_report": (
                results["about_the_report"] if "about_the_report" in results else None
            ),
            "materiality": results["materiality"] if "materiality" in results else None,
            "screen_nine_data": (
                results["screen_nine_data"] if "screen_nine_data" in results else None
            ),
            "screen_ten_data": (
                results["screen_ten_data"] if "screen_ten_data" in results else None
            ),
            "screen_eleven_data": (
                results["screen_eleven_data"]
                if "screen_eleven_data" in results
                else None
            ),
            "screen_twelve_data": (
                results["screen_twelve_data"]
                if "screen_twelve_data" in results
                else None
            ),
            "screen_thirteen_data": (
                results["screen_thirteen_data"]
                if "screen_thirteen_data" in results
                else None
            ),
            "screen_fourteen_data": (
                results["screen_fourteen_data"]
                if "screen_fourteen_data" in results
                else None
            ),
            "screen_fifteen_data": (
                results["screen_fifteen_data"]
                if "screen_fifteen_data" in results
                else None
            ),
            "materiality_table_data": materiality_table_data,
            "content_index_data": content_index_data,
            "pk": pk,  # Pass the report ID to the template
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
