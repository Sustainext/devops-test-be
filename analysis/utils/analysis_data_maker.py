from analysis.utils.Social.emloyment import employment_analysis, parental_leave_analysis
from analysis.utils.Social.ohs import (
    ohs_employee_worker_data,
    ohs_the_number_of_injuries,
)
from analysis.utils.Social.illhealth import ill_health_report_analysis
from analysis.utils.Social.organisation_governance_bodies import (
    create_data_for_organisation_governance_bodies,
)
from datametric.models import RawResponse


def create_analysis_data(raw_response: RawResponse):
    employment_analysis(raw_response=raw_response)
    parental_leave_analysis(raw_response=raw_response)
    ohs_employee_worker_data(raw_response=raw_response)
    ohs_the_number_of_injuries(raw_response=raw_response)
    ill_health_report_analysis(raw_response=raw_response)
    create_data_for_organisation_governance_bodies(raw_response=raw_response)
