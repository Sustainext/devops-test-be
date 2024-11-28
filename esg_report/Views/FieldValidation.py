from esg_report.models.ScreenOne import CeoMessage
from esg_report.models.ScreenTwo import AboutTheCompanyAndOperations
from esg_report.models.ScreenThree import MissionVisionValues
from esg_report.models.ScreenFour import SustainabilityRoadmap
from esg_report.models.ScreenFive import AwardAndRecognition
from esg_report.models.ScreenSix import StakeholderEngagement
from esg_report.models.ScreenSeven import AboutTheReport
from esg_report.models.ScreenEight import MaterialityStatement
from esg_report.models.ScreenNine import ScreenNine
from esg_report.models.ScreenTen import ScreenTen
from esg_report.models.ScreenEleven import ScreenEleven
from esg_report.models.ScreenTwelve import ScreenTwelve
from esg_report.models.ScreenThirteen import ScreenThirteen
from esg_report.models.ScreenFourteen import ScreenFourteen
from esg_report.models.ScreenFifteen import ScreenFifteenModel
from esg_report.Views.DummyValidationResponse import dummy_response_data
from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.response import Response
from sustainapp.models import Report
from collections import defaultdict
from functools import reduce
from operator import or_
from django.db.models import JSONField


class FieldValidationView(APIView):

    def filter_screen_data(self, model, report_id, json_fields):
        """Validate the fields in the data."""
        base_query = Q(report__id=report_id)

        json_field_queries = reduce(
            or_,
            [
                Q(**{f"{field}__content__isnull": True})
                | Q(**{f"{field}__content": ""})
                | Q(**{f"{field}__isSkipped": False})
                for field in json_fields
            ],
        )

        final_query = base_query & json_field_queries

        results = model.objects.filter(final_query).distinct()

        return results

    def process_screen_results(self, results, json_fields):
        """
        Process and format results for a screen.

        Args:
            results: QuerySet of results from a screen model.
            json_fields: List of JSON fields to process.

        Returns:
            List of formatted results.
        """
        formatted_results = []
        for result in results:
            for field in json_fields:
                field_data = getattr(result, field, None)
                if (
                    field_data
                    and field_data.get("isSkipped") == False
                    and (
                        field_data.get("content") is None
                        or field_data.get("content") == ""
                    )
                ):
                    formatted_results.append(
                        {
                            "page": field_data.get("page", ""),
                            "label": field_data.get("label", ""),
                            "subLabel": field_data.get("subLabel", ""),
                            "type": field_data.get("type", ""),
                            "content": field_data.get("content", ""),
                            "field": field_data.get("field", ""),
                            "isSkipped": field_data.get("isSkipped", ""),
                        }
                    )
        return formatted_results

    def get_json_fields(self, model):
        """Get all JSON fields of a model except the `report` field."""
        return [
            field.name
            for field in model._meta.get_fields()
            if isinstance(field, JSONField)
        ]

    def get(self, request, report_id):
        """Handle GET request to validate fields.
        Checked if the report exists.
        checks If model has data related to  the report.
        If the model has data related to the report, it filters the data based on the JSON fields.
        It then processes the results and formats them for the response.
        If the model does not have data related to the report, it returns dummy responses.
        """

        # if not Report.objects.filter(id=report_id).exists():
        #     return Response({"error": "Report not found"}, status=404)

        combined_results = []
        dummy_responses = dummy_response_data

        screens = {
            "screen_one": {
                "model": CeoMessage,
                "fields": self.get_json_fields(CeoMessage),
            },
            "screen_two": {
                "model": AboutTheCompanyAndOperations,
                "fields": self.get_json_fields(AboutTheCompanyAndOperations),
            },
            "screen_three": {
                "model": MissionVisionValues,
                "fields": self.get_json_fields(MissionVisionValues),
            },
            "screen_four": {
                "model": SustainabilityRoadmap,
                "fields": self.get_json_fields(SustainabilityRoadmap),
            },
            "screen_five": {
                "model": AwardAndRecognition,
                "fields": self.get_json_fields(AwardAndRecognition),
            },
            "screen_six": {
                "model": StakeholderEngagement,
                "fields": self.get_json_fields(StakeholderEngagement),
            },
            "screen_seven": {
                "model": AboutTheReport,
                "fields": self.get_json_fields(AboutTheReport),
            },
            "screen_eight": {
                "model": MaterialityStatement,
                "fields": self.get_json_fields(MaterialityStatement),
            },
            "screen_nine": {
                "model": ScreenNine,
                "fields": self.get_json_fields(ScreenNine),
            },
            "screen_ten": {
                "model": ScreenTen,
                "fields": self.get_json_fields(ScreenTen),
            },
            "screen_eleven": {
                "model": ScreenEleven,
                "fields": self.get_json_fields(ScreenEleven),
            },
            "screen_twelve": {
                "model": ScreenTwelve,
                "fields": self.get_json_fields(ScreenTwelve),
            },
            "screen_thirteen": {
                "model": ScreenThirteen,
                "fields": self.get_json_fields(ScreenThirteen),
            },
            "screen_fourteen": {
                "model": ScreenFourteen,
                "fields": self.get_json_fields(ScreenFourteen),
            },
            "screen_fifteen": {
                "model": ScreenFifteenModel,
                "fields": self.get_json_fields(ScreenFifteenModel),
            },
        }

        for screen_name, screen_data in screens.items():
            model = screen_data["model"]
            json_fields = screen_data["fields"]

            results = model.objects.filter(report__id=report_id)

            if results.exists():
                processed_results = self.process_screen_results(results, json_fields)

                for field in json_fields:
                    if not model.objects.filter(
                        report__id=report_id, **{f"{field}__isnull": False}
                    ).exists():
                        if screen_name in dummy_responses:
                            dummy_field_data = [
                                d
                                for d in dummy_responses[screen_name]
                                if d["field"] == field
                            ]
                            processed_results.extend(dummy_field_data)

                combined_results.extend(processed_results)
            else:
                if screen_name in dummy_responses:
                    combined_results.extend(dummy_responses[screen_name])

        return Response(combined_results)
