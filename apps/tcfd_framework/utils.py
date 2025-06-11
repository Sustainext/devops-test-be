from apps.tcfd_framework.models.TCFDCollectModels import (
    CoreElements,
    DataCollectionScreen,
    RecommendedDisclosures,
)


# 1. Core Elements
core_elements_data = [
    {
        "name": "Governance",
        "description": "Disclose the organization’s governance around climate related risks and opportunities.",
    },
    {
        "name": "Strategy",
        "description": "Disclose the actual and potential impacts of climate-related risks and opportunities on the organization’s businesses, strategy, and financial planning where such information is material.",
    },
    {
        "name": "Risk Management",
        "description": "Disclose how the organization identifies, assesses, and manages climate-related risks.",
    },
    {
        "name": "Metrics & Targets",
        "description": "Disclose the metrics and targets used to assess and manage relevant climate-related risks and opportunities where such information is material.",
    },
]

core_element_objs = {}
for elem in core_elements_data:
    obj, _ = CoreElements.objects.get_or_create(
        name=elem["name"], defaults={"description": elem["description"]}
    )
    core_element_objs[elem["name"]] = obj

# 2. Recommended Disclosures and Data Collection Screens
disclosures_data = [
    # Governance
    {
        "core": "Governance",
        "order": 0,
        "description": "Describe the board’s oversight of climate-related risks and opportunities.",
        "screens": [
            "Structure",
            "Board’s oversight of climate related risks and opportunities",
        ],
    },
    {
        "core": "Governance",
        "order": 1,
        "description": "Describe management’s role in assessing and managing climate-related risks and opportunities.",
        "screens": [
            "Structure",
            "Management’s role in assessing and managing climate related risks and opportunities",
        ],
    },
    # Strategy
    {
        "core": "Strategy",
        "order": 0,
        "description": "Describe the climate-related risks and opportunities the organization has identified over the short, medium, and long term.",
        "screens": ["Climate related Risks", "Climate related Opportunities"],
    },
    {
        "core": "Strategy",
        "order": 1,
        "description": "Describe the impact of climate-related risks and opportunities on the organization’s businesses, strategy, and financial planning.",
        "screens": ["Impact of Climate Related Issues on Business"],
    },
    {
        "core": "Strategy",
        "order": 2,
        "description": "Describe the resilience of the organization’s strategy, taking into consideration different climate-related scenarios, including a 2°C or lower scenario.",
        "screens": ["Resilience of the Organisation’s Strategy"],
    },
    # Risk Management
    {
        "core": "Risk Management",
        "order": 0,
        "description": "Describe the organization’s processes for identifying and assessing climate-related risks.",
        "screens": ["Risk Identification & Assessment"],
    },
    {
        "core": "Risk Management",
        "order": 1,
        "description": "Describe the organization’s processes for managing climate-related risks.",
        "screens": ["Climate Risk Management"],
    },
    {
        "core": "Risk Management",
        "order": 2,
        "description": "Describe how processes for identifying, assessing, and managing climate-related risks are integrated into the organization’s overall risk management.",
        "screens": ["Climate Risk Integration"],
    },
    # Metrics & Targets
    {
        "core": "Metrics & Targets",
        "order": 0,
        "description": "Disclose the metrics used by the organization to assess climate-related risks and opportunities in line with its strategy and risk management process.",
        "screens": ["Climate Related Metrics"],
    },
    {
        "core": "Metrics & Targets",
        "order": 1,
        "description": "Disclose Scope 1, Scope 2, and, if appropriate, Scope 3 greenhouse gas (GHG) emissions, and the related risks.",
        "screens": ["GHG Emissions", "GHG Emission Intensity"],
    },
    {
        "core": "Metrics & Targets",
        "order": 2,
        "description": "Describe the targets used by the organization to manage climate-related risks and opportunities and performance against targets.",
        "screens": ["Climate Related Targets"],
    },
]

for disclosure in disclosures_data:
    core_element = core_element_objs[disclosure["core"]]
    rec_disc, _ = RecommendedDisclosures.objects.get_or_create(
        description=disclosure["description"],
        core_element=core_element,
        defaults={
            "order": disclosure["order"],
            "screen_tag": None,
        },
    )
    rec_disc.save()
    order = 0
    for screen_name in disclosure["screens"]:
        data_collection_screen_object, _ = DataCollectionScreen.objects.get_or_create(
            name=screen_name, recommended_disclosure=rec_disc, order=order
        )
        data_collection_screen_object.save()
        order += 1
