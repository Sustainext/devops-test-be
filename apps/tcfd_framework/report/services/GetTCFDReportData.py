from apps.tcfd_framework.report.models import TCFDReport
from datametric.models import DataPoint
from sustainapp.report import Report


class GetTCFDReportData:
    """
    This service files gets you collect data based on the screen_name
    """

    def __init__(self, report: Report):
        self.report = report

    def add_data(self):
        screen_wise_mapping = {
            "message_ceo": {
                "company_name": self.report.organization.name,
            },
            "about_report": [],
            "about_company": [],
            "governance": {
                "committees_of_the_highest_governance_body": "gri-governance-structure-2-9-b-committees",
                "boards_oversight_of_climate_related_risks_and_opportunities": "governance-board-involvement-in-sustainability-boards-oversight-of-climate-related-risks-and-opportunities",
                "governance_structure": "gri-governance-structure-2-9-a-governance_structure",
                "managements_role_in_assessing_and_managing_climate_related_risks_and_opportunities": "governance-governance-managements-role-in-assessing-and-managing-climate-related-risks-and-opportunities",
            },
            "strategy": {
                "physical_risks": "gri-economic-climate_related_risks-202-2a-physical_risk",
                "transition_risk": "gri-economic-climate_related_risks-202-2a-transition_risk",
                "other_risks": "gri-economic-climate_related_risks-202-2a-other_risk",
            },
            "risk_management": [],
            "metrics_targets": [],
            "tcfd_content_index": [],
            "annexure": [],
        }

    def get_data_as_per_screen(self, screen_name: str): ...
