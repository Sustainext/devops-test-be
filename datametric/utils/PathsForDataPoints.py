"""
For type1 :
Include all the paths here where the data points are created but they are
begin overwritten creating DataPoits only the last dictionary in the list.

For the below example the data points wil be created for 1st dictionary but
will be overwritten by the 2nd dictionary and this continues till the end of
the list we will be only left with data ponits being created for the last dictionary.
Example :
[
  {
    "benefits": [
      {
        "name": "Life Insurance",
        "selectedLocations": [3,4,5],
        "removable": false,
        "editable": false,
        "selected": true
      },
      {
        "name": "Disability & Invalidity Coverage",
        "selectedLocations": [3,4,5],
        "removable": false,
        "editable": false,
        "selected": true
      },
      {
        "name": "Retirement Provision",
        "selectedLocations": [],
        "removable": false,
        "editable": false,
        "selected": false
      }
    ]
  }
]

There are some more cases handled here Please check the "Discrepancies in DataPoints.xlsx" or
check with the developers/team lead to get the excel file.
"""

type1_paths = {
    "gri-social-benefits-401-2a-benefits_provided_tab_1": "",
    "gri-social-benefits-401-2a-benefits_provided_tab_2": "",
    "gri-social-benefits-401-2a-benefits_provided_tab_3": "",
    "gri-governance-implementing-commitments-2-24-a-describe": "",
    "gri-governance-determine-remuneration-2-20-a-process": "",
    "gri-governance-chair_of_board-2-11-b-chair": "",
    "gri-economic-climate_related_risks-202-2a-physical_risk": "",
    "gri-economic-climate_related_risks-202-2a-transition_risk": "",
    "gri-environment-water-303-3b-4c-water_withdrawal/discharge_areas_water_stress": "",
    "gri-environment-water-303-5c-change_in_water_storage": "",
    "gri-social-performance_and_career-414-2b-number_of_suppliers": "",
    "gri-social-salary_ratio-405-2a-number_of_individuals": "",
    "gri-social-salary_ratio-405-2a-ratio_of_remuneration": "",
}

type2_paths = {
    "gri-governance-remuneration-2-19-a-remuneration": "",
}

type3_paths = {
    "gri-governance-structure-2-9-b-committees": "",
    "gri-economic-country_by_country_reporting-207-4a-please": "",
}

type4_path = {"gri-general-org_details_2-1a-1b-1c-1d": ""}


all_type_paths = {
    **type1_paths,
    **type2_paths,
    **type3_paths,
    **type4_path,
}
