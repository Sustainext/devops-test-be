from sustainapp.report import Report
from common.utils.data_point_cache import get_data_point_cache
from apps.tcfd_framework.utils import get_or_set_tcfd_cache_data
from common.utils.report_datapoint_utils import (
    get_data_points_as_per_report,
    get_emission_analysis_as_per_report,
    get_emission_analyse_as_per_report,
    get_emission_analysis_data_as_per_report,
)
from common.utils.get_data_points_as_raw_responses import (
    collect_data_by_raw_response_and_index,
)


class GetTCFDReportData:
    """
    This service files gets you collect data based on the screen_name
    """

    def __init__(self, report: Report):
        self.report = report
        self.start_date = self.report.start_date
        self.end_date = self.report.end_date
        self.organization = self.report.organization
        self.corporate = self.report.corporate

    def get_mapping(self):
        return {
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
            "tcfd_content_index": get_or_set_tcfd_cache_data(
                organization=self.report.organization, corporate=self.report.corporate
            ),
            "annexure": {
                "size_scope_of_risk": "governance-risk-management-risk-identification-assessment-screen4"
            },
        }

    def get_collect_data(self, topic_slug_mapping: dict, data_points):
        collect_data = {}
        for topic_name, slug in topic_slug_mapping.items():
            data_point_ids = list(
                data_points.filter(path__slug=slug).values_list("id", flat=True)
            )
            collect_data[topic_name] = collect_data_by_raw_response_and_index(
                data_points=data_point_ids
            )
        return collect_data

    def get_data_as_per_screen(self, screen_name: str):
        try:
            mapped_data = self.get_mapping()[screen_name]
            data_points = get_data_points_as_per_report(report=self.report)
            slug_keys = [
                "governance",
                "strategy",
                "risk_management",
                "metrics_targets",
                "annexure",
            ]
            if screen_name not in slug_keys:
                return mapped_data
            else:
                mapped_data = self.get_collect_data(
                    topic_slug_mapping=mapped_data, data_points=data_points
                )
                if screen_name == "metrics_targets":
                    mapped_data["emission_analyse"] = (
                        get_emission_analyse_as_per_report(
                            report=self.report, data_points=data_points
                        )
                    )
                    emission_report_data = get_emission_analysis_data_as_per_report(
                        report=self.report
                    )
                    mapped_data.update(
                        {
                            "scope_1": emission_report_data[
                                "gri-environment-emissions-301-a-scope-1"
                            ],
                            "scope_2": emission_report_data[
                                "gri-environment-emissions-301-a-scope-2"
                            ],
                            "scope_3": emission_report_data[
                                "gri-environment-emissions-301-a-scope-3"
                            ],
                        }
                    )

                return mapped_data
        except KeyError:
            mapped_data = None
