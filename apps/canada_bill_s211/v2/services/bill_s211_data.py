from apps.canada_bill_s211.v2.models.SubmissionInformation import SubmissionInformation
from apps.canada_bill_s211.v2.models.ReportingForEntities import ReportingForEntities
from apps.canada_bill_s211.v2.models.BillS211Report import BillS211Report
from sustainapp.models import Report
from apps.canada_bill_s211.v2.serializers.SubmissionInformationSerializer import SubmissionInformationSerializer
from apps.canada_bill_s211.v2.serializers.ReportingForEntitiesSerializer import ReportingForEntitiesSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError

class BillS211ScreenDataService:
    def __init__(self, report: Report, screen:int):
        self.report = report
        self.organization = self.report.organization
        self.corporate = self.report.corporate
        self.year = self.report.end_date.year
        self.screen = screen
        self.submission_information = (
            SubmissionInformation.objects.filter(organization=self.organization,
                corporate=self.corporate,
                year=self.year,
            )
        )
        self.reporting_for_entities = (
            ReportingForEntities.objects.filter(organization=self.organization,
                        corporate=self.corporate,
                        year=self.year,
                    )
                )
        self.not_available = "NA"


    def get_report_data(self):
        try:
            self.canada_report = BillS211Report.objects.get(report=self.report, screen=self.screen)
            report_data = self.canada_report.data
        except ObjectDoesNotExist:
            report_data = None
        return report_data


    def get_all_data(self):
        submission_information = (
            SubmissionInformation.objects.filter(organization=self.organization,
                corporate=self.corporate,
                year=self.year,
            )
        )

        reporting_for_entities = (
            ReportingForEntities.objects.filter(organization=self.organization,
                        corporate=self.corporate,
                        year=self.year,
                    )
                )
        response = {
        "report_data":[],
        "collect_data_part_1":[],
        "collect_data_part_2":[],
        "complete_response_part_1":[],
        "complete_response_part_2":[]

        }
        for submission_information_data in SubmissionInformationSerializer(submission_information, many=True).data:
            response["collect_data_part_1"].append(
                {
                    "screen":submission_information_data["screen"],
                    "data":submission_information_data["data"]
                }
            )

        for reporting_for_entities_data in ReportingForEntitiesSerializer(reporting_for_entities, many=True).data:
            response["collect_data_part_2"].append(
                {
                    "screen": reporting_for_entities_data["screen"],
                    "data":reporting_for_entities_data["data"]
                }
            )

        for submission_information_data in SubmissionInformationSerializer(submission_information, many=True).data:
            response["complete_response_part_1"].append(submission_information_data)

        for reporting_for_entities_data in ReportingForEntitiesSerializer(reporting_for_entities, many=True).data:
            response["complete_response_part_2"].append(reporting_for_entities_data)


        return response

    def get_screen_zero_data(self):
        data = self.submission_information.get(screen=1).data
        return {
            "p1_q1":data.get("screen1_q2",self.not_available),
        }

    def get_screen_one_data(self):
        data = self.submission_information.get(screen=1).data
        return {
            "p1_q1":data.get("screen1_q2",self.not_available),
            "p1_q4":f"{data.get('screen1_to_q4',self.not_available)}-{data.get('screen1_form_q4',self.not_available)}"
        }
