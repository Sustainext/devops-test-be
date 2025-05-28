from apps.canada_bill_s211.v2.models.SubmissionInformation import SubmissionInformation
from apps.canada_bill_s211.v2.models.BillS211Report import BillS211Report
from apps.canada_bill_s211.v2.serializers.SubmissionInformationSerializer import SubmissionInformationSerializer

class BillS211ScreenDataService:
    def __init__(self, report: BillS211Report):
        self.canada_report = report
        self.report = self.canada_report.report
        self.organization = self.report.organization
        self.corporate = self.report.corporate
        self.year = self.report.to_year.year

    def get_introduction_page_data(self):
        submission_information = (
            SubmissionInformation.objects.filter(organization=self.organization,
                corporate=self.corporate,
                year=self.year,
            )
        )

        part_1_question_2 = submission_information.get(screen=1)
        return SubmissionInformationSerializer(part_1_question_2).data
