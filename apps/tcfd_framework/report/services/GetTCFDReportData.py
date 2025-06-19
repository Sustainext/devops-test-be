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
                "general_business_impact": "impact-of-climate-related-issues-on-business",
                "ghg_emissions_reduction_commitments": "gri-governance-management_of_impact-2-12-b-due_diligence",
                "strategy_resilience_to_climate_related_risks_and_opportunities": "economic-climate-risks-and-opportunities-resilience-of-the-organisations-strategy",
            },
            "risk_management": {
                "climate_related_risk_identification_assessment_process": "governance-risk-management-risk-identification-assessment-screen1",
                "risk_significance": "governance-risk-management-risk-identification-assessment-screen2",
                "regulatory_considerations": "governance-risk-management-risk-identification-assessment-screen3",
                "size_scope_of_risk": "governance-risk-management-risk-identification-assessment-screen4",
                "climate_risks_integration_into_organisations_risk_management_framework": "governance-risk-management-climate-risk-integration",
                "climate_risk_management_process": "governance-risk-management-climate-risk-management-screen1",
                "materiality_determination": "governance-risk-management-climate-risk-management-screen2",
            },
            "metrics_targets": {
                "metrics_used_to_assess_climate_related_risks_and_opportunities": "economic-climate-risks-and-opportunities-climate-related-metrics",
                "metrics_used_to_assess_climate_related_opportunities": "economic-climate-risks-and-opportunities-climate-related-metrics-screen2",
                "targets_used_to_manage_climate_related_risks_and_opportunities_and_performance_against_targets": "economic-climate-risks-and-opportunities-climate-related-targets",
            },
            "tcfd_content_index": [],
            "annexure": [],
        }

    def get_data_as_per_screen(self, screen_name: str):...
