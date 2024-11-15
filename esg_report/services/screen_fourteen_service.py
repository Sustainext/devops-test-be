from esg_report.utils import (
    get_raw_responses_as_per_report,
    get_data_points_as_per_report,
    get_maximum_months_year,
    collect_data_by_raw_response_and_index,
    collect_data_and_differentiate_by_location,
    forward_request_with_jwt,
)
from django.core.exceptions import ObjectDoesNotExist
from sustainapp.Utilities.community_engagement_analysis import (
    get_community_engagement_analysis,
)
from esg_report.Serializer.ScreenFourteenSerializer import ScreenFourteenSerializer
from sustainapp.models import Report
from esg_report.models.ScreenFourteen import ScreenFourteen


class ScreenFourteenService:
    def __init__(self, report_id, request):
        self.report = Report.objects.get(id=report_id)
        self.request = request
        self.slugs = {0: "gri-social-impact_on_community-407-1a-operations"}

    def set_data_points(self):
        self.data_points = get_data_points_as_per_report(self.report)

    def set_raw_responses(self):
        self.raw_responses = get_raw_responses_as_per_report(self.report)

    def get_413_1a(self):
        slug = {0: "gri-social-community_engagement-413-1a-number_of_operations"}
        raw_responses = self.raw_responses.filter(path__slug=slug[0])
        return get_community_engagement_analysis(
            raw_responses=raw_responses, slugs=slug
        )

    def get_api_response(self):
        response_data = {}
        try:
            screen_fourteen: ScreenFourteen = self.report.screen_fourteen
            serializer = ScreenFourteenSerializer(
                screen_fourteen, context={"request": self.request}
            )
            response_data.update(serializer.data)
        except ObjectDoesNotExist:
            response_data.update(
                {
                    field.name: None
                    for field in ScreenFourteen._meta.fields
                    if field.name not in ["id", "report"]
                }
            )
        self.set_data_points()
        self.set_raw_responses()
        response_data["413_2a"] = collect_data_and_differentiate_by_location(
            self.data_points.filter(path__slug=self.slugs[0])
        )
        response_data["413_1a_analyse"] = self.get_413_1a()
        response_data["3_3cde"] = (
            None  # TODO: Complete when materiality assessment screen is ready.
        )
        return response_data

    def get_report_response(self):
        response_data = self.get_api_response()
        response_data = {
            key.replace("-", "_"): value for key, value in response_data.items()
        }
        return response_data
