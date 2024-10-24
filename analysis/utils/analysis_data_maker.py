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
from analysis.utils.Water.water_from_all_areas_analysis import (
    create_data_for_water_from_all_areas_analysis,
    create_data_for_water_discharge_from_third_party,
)
from analysis.utils.Water.water_from_stress_areas import (
    create_data_for_water_from_stress_areas,
    create_data_for_water_discharge_from_stress_areas,
)
from analysis.utils.Water.change_in_water_storage import (
    create_data_for_change_in_water_storage,
)
from analysis.utils.Material.material_weight_or_volume import (
    create_data_for_non_renewable_materials,
)
from analysis.utils.Material.recycled_input_materials import (
    create_data_for_recycled_input_materials,
)
from analysis.utils.Material.reclaimed_materials import (
    create_data_for_reclaimed_materials,
)
from analysis.utils.Governance.compensation import fill_data_inside_compensation
from analysis.utils.Governance.compensation_increase import fill_data_inside_compensation_increase
from datametric.models import RawResponse
from analysis.utils.General.CollectiveBargainingAnalyze import (
    create_data_for_general_collective_bargaining,
)
from analysis.utils.General.WorkForceEmpAnalyze import (
    total_number_employees_analysis,
)
from analysis.utils.General.WorkForceOtherWorkersAnalyze import (
    workforce_other_workers_analysis,
)
from analysis.utils.Economic.CommunicationAndTrainingAnalyze import (
    create_data_for_economic_total_body_members,
    create_data_for_economic_total_body_members_region,
)
from analysis.utils.Economic.MarketPresenceAnalyze import (
    create_data_for_economic_standard_wages,
)

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
    create_data_for_water_from_all_areas_analysis(raw_response=raw_response)
    create_data_for_water_from_stress_areas(raw_response=raw_response)
    create_data_for_water_discharge_from_stress_areas(raw_response=raw_response)
    create_data_for_water_discharge_from_third_party(raw_response=raw_response)
    create_data_for_change_in_water_storage(raw_response=raw_response)
    create_data_for_non_renewable_materials(raw_response=raw_response)
    create_data_for_recycled_input_materials(raw_response=raw_response)
    create_data_for_reclaimed_materials(raw_response=raw_response)
    fill_data_inside_compensation(raw_response=raw_response)
    fill_data_inside_compensation_increase(raw_response=raw_response)
    create_data_for_general_collective_bargaining(raw_response=raw_response)
    total_number_employees_analysis(raw_response=raw_response)
    workforce_other_workers_analysis(raw_response=raw_response)
    create_data_for_economic_total_body_members(raw_response=raw_response)
    create_data_for_economic_total_body_members_region(raw_response=raw_response)
    create_data_for_economic_standard_wages(raw_response=raw_response)
