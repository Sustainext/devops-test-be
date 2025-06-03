from apps.canada_bill_s211.v2.models.SubmissionInformation import SubmissionInformation
from apps.canada_bill_s211.v2.models.ReportingForEntities import ReportingForEntities
from sustainapp.models import Report
from apps.canada_bill_s211.v2.serializers.SubmissionInformationSerializer import (
    SubmissionInformationSerializer,
)
from apps.canada_bill_s211.v2.serializers.ReportingForEntitiesSerializer import (
    ReportingForEntitiesSerializer,
)
from apps.canada_bill_s211.v2.models.BillS211Report import BillS211Report
from rest_framework.exceptions import ValidationError
import logging

logger = logging.getLogger("django")


class BillS211ScreenDataService:
    """
    Service file that gets data based on report and screen data.
    """

    def __init__(self, report: Report, screen: int):
        self.report = report
        self.organization = self.report.organization
        self.corporate = self.report.corporate
        self.year = self.report.end_date.year
        self.screen = screen
        self.submission_information = SubmissionInformation.objects.filter(
            organization=self.organization,
            corporate=self.corporate,
            year=self.year,
        )
        self.reporting_for_entities = ReportingForEntities.objects.filter(
            organization=self.organization,
            corporate=self.corporate,
            year=self.year,
        )
        self.not_available = "NA"
        self.page_to_json_mapping = {
            1: [
                "part_1_screen1_q2",
                "part_1_screen1_to_q4",
                "part_1_screen1_form_q4",
                "part_1_screen1_q3",
            ],  # P1-Q2
            2: [
                "part_1_screen1_q2",  # P1-Q2 (company name)
                "part_1_screen1_to_q4",  # P1-Q4 (calendar date input 1)
                "part_1_screen1_form_q4",  # P1-Q4 (calendar date input 2)
            ],
            3: [
                "part_1_screen1_q2",  # P1-Q2 (company name)
                "part_1_screen7_q1",  # P1-Q11 (headquarters location - screen7_q1 is Canada)
                "part_1_screen5_q1",  # P1-Q9 (dropdown options - listed on stock exchange)
                "part_1_screen1_to_q4",  # P1-Q4 (calendar date)
                "part_1_screen1_form_q4",  # P1-Q4 (calendar date)
                "part_2_screen1_q2",  # P2-Q2 (business activities)
            ],
            4: [
                "part_1_screen1_q2",  # P1-Q2 (company name)
                "part_2_screen1_q2",  # P2-Q2 (business activities)
            ],
            5: [
                "part_1_screen1_q2",  # P1-Q2 (company name)
                "part_2_screen3_q1",  # P2-Q5 (policies question)
                "part_2_screen3_q2",  # P2-Q5_1 (due diligence processes)
                "part_2_screen4_q1",  # P2-Q6 (risks identification)
                "part_2_screen4_q2",  # P2-Q6_1 (risk aspects)
                "part_2_screen5_q1",  # P2-Q7 (sector/industry risks)
                "part_2_screen5_q3",  # P2-Q8 (additional risk info)
            ],
            6: [
                "part_1_screen1_q2",  # P1-Q2 (company name)
                "part_2_screen4_q1",  # P2-Q6 (risks identification)
                "part_2_screen4_q2",  # P2-Q6_1 (risk aspects)
                "part_2_screen5_q1",  # P2-Q7 (sector/industry risks)
                "part_2_screen5_q3",  # P2-Q8 (additional risk info)
                "part_2_screen2_q1",  # P2-Q3 (steps taken to prevent risks)
            ],
            7: [
                "part_2_screen2_q1",  # P2-Q3 (steps taken)
                "part_2_screen2_q2",  # P2-Q4 (additional steps info)
                "part_2_screen6_q1",  # P2-Q9 (remediation measures)
                "part_2_screen6_q2",  # P2-Q9_1 (remediation details)
            ],
            8: [
                "part_1_screen1_q2",  # P1-Q2 (company name)
                "part_2_screen2_q2",  # P2-Q4 (additional steps info)
                "part_2_screen7_q2",  # P2-Q11 (training provided)
                "part_2_screen7_q3",  # P2-Q11_1 (training scope/mandatory)
            ],
            9: [
                "part_1_screen1_q2",  # P1-Q2 (company name)
                "part_2_screen8_q1",  # P2-Q12 (effectiveness assessment)
                "part_2_screen8_q2",  # P2-Q12_1 (effectiveness measures)
            ],
            10: ["part_1_screen1_q2"],  # P1-Q2 (company name)
            11: ["part_1_screen1_q2"],  # P1-Q2 (company name)
            12: [],  # Legend page
        }

    def get_all_data(self):
        """
        Gets all the data from the database.
        """
        submission_information = SubmissionInformation.objects.filter(
            organization=self.organization,
            corporate=self.corporate,
            year=self.year,
        )

        reporting_for_entities = ReportingForEntities.objects.filter(
            organization=self.organization,
            corporate=self.corporate,
            year=self.year,
        )
        data = {}

        for submission_information_data in SubmissionInformationSerializer(
            submission_information, many=True
        ).data:
            prefixed_data = {
                f"part_1_{key}": value
                for key, value in submission_information_data["data"].items()
            }
            data.update(prefixed_data)

        for reporting_for_entities_data in ReportingForEntitiesSerializer(
            reporting_for_entities, many=True
        ).data:
            prefixed_data = {
                f"part_2_{key}": value
                for key, value in reporting_for_entities_data["data"].items()
            }
            data.update(prefixed_data)

        return data

    def get_screen_wise_data(self):
        """
        Gets screen wise data.
        """
        data = self.get_all_data()
        response = {}
        try:
            for i in self.page_to_json_mapping[self.screen]:
                response[i] = data.get(i, self.not_available)
        except KeyError as e:
            logger.error(e)
            raise ValidationError("Page Number not defined in report.")
        # * Add report data.
        response.update({"report_data": self.get_report_data()})
        return response

    def get_report_data(self):
        try:
            return BillS211Report.objects.get(
                report=self.report, screen=self.screen
            ).data
        except BillS211Report.DoesNotExist:
            return {}
