from analysis.utils.Social.emloyment import employment_analysis, parental_leave_analysis
from analysis.utils.Social.ohs import (
    ohs_employee_worker_data,
    ohs_the_number_of_injuries,
)
from analysis.utils.Social.illhealth import ill_health_report_analysis
from analysis.utils.Social.organisation_governance_bodies import (
    create_data_for_organisation_governance_bodies,
)
from analysis.utils.Social.governance_body_details import (
    create_data_for_governance_bodies_details,
)
from analysis.utils.Social.community_development_number_of_operations import (
    create_data_for_community_development_number_of_operations,
)
from analysis.utils.Waste.waste_generated_analysis import (
    create_data_for_waste_generated_analysis,
)
from analysis.utils.Waste.waste_diverted_from_disposal_analysis import (
    create_data_for_waste_diverted_from_disposal_analysis,
)
from analysis.utils.Waste.waste_directed_to_disposal_analysis import (
    create_data_for_waste_diverted_to_disposal_analysis,
)
from analysis.utils.Energy.reduction_in_energy_product_services_analysis import (
    create_data_for_reduction_in_energy_product_services,
)
from analysis.utils.Energy.energy_consumed_within_org import (
    create_data_for_direct_purchased_energy,
    create_data_for_consumed_energy,
    create_data_for_self_genereted,
    create_data_for_energy_sold,
)
from analysis.utils.Energy.reduction_in_energy_consumption import (
    create_data_for_reduction_in_energy_consumption,
)
from analysis.utils.Energy.energy_intensity_analysis import (
    create_data_for_energy_intensity_analysis,
)
from analysis.utils.Energy.energy_consumed_outside_org import (
    create_data_for_energy_consumed_outsid_org_analysis,
)
from analysis.utils.Environment.updating_emission_data import updating_emission_data
from datametric.models import RawResponse


def create_analysis_data(raw_response: RawResponse):
    employment_analysis(raw_response=raw_response)
    parental_leave_analysis(raw_response=raw_response)
    ohs_employee_worker_data(raw_response=raw_response)
    ohs_the_number_of_injuries(raw_response=raw_response)
    ill_health_report_analysis(raw_response=raw_response)
    create_data_for_organisation_governance_bodies(raw_response=raw_response)
    create_data_for_governance_bodies_details(raw_response=raw_response)
    create_data_for_community_development_number_of_operations(
        raw_response=raw_response
    )
    create_data_for_waste_generated_analysis(raw_response=raw_response)
    create_data_for_waste_diverted_from_disposal_analysis(raw_response=raw_response)
    create_data_for_waste_diverted_to_disposal_analysis(raw_response=raw_response)
    create_data_for_reduction_in_energy_product_services(raw_response=raw_response)
    create_data_for_direct_purchased_energy(raw_response=raw_response)
    create_data_for_consumed_energy(raw_response=raw_response)
    create_data_for_self_genereted(raw_response=raw_response)
    create_data_for_energy_sold(raw_response=raw_response)
    create_data_for_energy_consumed_outsid_org_analysis(raw_response=raw_response)
    create_data_for_reduction_in_energy_consumption(raw_response=raw_response)
    create_data_for_energy_intensity_analysis(raw_response=raw_response)
    updating_emission_data(raw_response=raw_response)
