from materiality_dashboard.models import MaterialTopic, Disclosure


def load_identifiers(material_topics):
    count = 0
    for key in material_topics:
        try:
            m = MaterialTopic.objects.filter(name__icontains=key[1])
            for i in m:
                i.identifier = key[0]
                i.save()
            count += 1
        except MaterialTopic.DoesNotExist:
            print(f"MaterialTopic {key[0]} does not exist")
    print(count)


material_topics = {
    ("EnvGhgEmission", "GHG Emissions"): [
        ("305-1 Direct (Scope 1) GHG emissions", "EnvGhgEmission305-1"),
        ("305-2 Energy indirect (Scope 2) GHG emissions", "EnvGhgEmission305-2"),
        ("305-3 Other indirect (Scope 3) GHG emissions", "EnvGhgEmission305-3"),
        ("305-4 GHG emissions intensity", "EnvGhgEmission305-4"),
        ("305-5 Reduction of GHG emissions", "EnvGhgEmission305-5"),
    ],
    ("EnvBioDiversityLandUse", "Biodiversity & land use"): [
        (
            "304-2 Significant impacts of activities, products and services on biodiversity",
            "EnvBioDiversityLandUse304-2",
        ),
        ("304-3 Habitats protected or restored", "EnvBioDiversityLandUse304-3"),
        (
            "304-4 IUCN Red List species and national conservation list species with habitats in areas affected by operations",
            "EnvBioDiversityLandUse304-4",
        ),
    ],
    ("EnvAirQuality", "Air Quality"): [
        (
            "305-7 Nitrogen oxides (NOx), sulfur oxides (SOx), and other significant air emissions",
            "EnvAirQuality305-7",
        )
    ],
    ("EnvWaterEffluent", "Water & effluent"): [
        (
            "303-2 Management of water discharge-related impacts",
            "EnvWaterEffluent303-2",
        ),
        ("303-3 Water withdrawal", "EnvWaterEffluent303-3"),
        ("303-4 Water discharge", "EnvWaterEffluent303-4"),
        ("303-5 Water consumption", "EnvWaterEffluent303-5"),
    ],
    ("EnvRawMaterialSourcing", "Raw Material Sourcing "): [
        ("301-2 Recycled input materials used", "EnvRawMaterialSourcing301-2")
    ],
    ("EnvWasteManagement", "Waste Management "): [
        (
            "306-2 Management of significant waste-related impacts",
            "EnvWasteManagement306-2",
        ),
        ("306-3 Waste generated", "EnvWasteManagement306-3"),
        ("306-4 Waste diverted from disposal", "EnvWasteManagement306-4"),
        ("306-5 Waste directed to disposal", "EnvWasteManagement306-5"),
    ],
    ("EnvEnergy", "Energy "): [
        ("302-2 Energy consumption outside of the organization", "EnvEnergy302-2"),
        ("302-3 Energy intensity", "EnvEnergy302-3"),
        ("302-4 Reduction of energy consumption", "EnvEnergy302-4"),
        (
            "302-5 Reductions in energy requirements of products and services",
            "EnvEnergy302-5",
        ),
    ],
    ("EnvSupplyChainSustainability", "Supply chain sustainability"): [
        (
            "308-2 Negative environmental impacts in the supply chain and actions taken",
            "EnvSupplyChain308-2",
        )
    ],
    ("EnvFossilFuel", "Fossil Fuel"): [
        ("GRI 12: Coal Sector 2022", "EnvFossilFuelGri12")
    ],
    ("SocHealthSafety", "Occupational Health &  Safety"): [
        (
            "403-2 Hazard identification, risk assessment, and incident investigation",
            "SocHealthSafety403-2",
        ),
        (
            "403-4 Worker participation, consultation, and communication on occupational health and safety",
            "SocHealthSafety403-4",
        ),
        (
            "403-5 Worker training on occupational health and safety",
            "SocHealthSafety403-5",
        ),
        ("403-6 Promotion of worker health", "SocHealthSafety403-6"),
        (
            "403-7 Prevention and mitigation of occupational health and safety impacts directly linked by business relationships",
            "SocHealthSafety403-7",
        ),
        (
            "403-8 Workers covered by an occupational health and safety management system",
            "SocHealthSafety403-8",
        ),
        ("403-9 Work-related injuries", "SocHealthSafety403-9"),
        ("403-10 Work-related ill health", "SocHealthSafety403-10"),
    ],
    ("SocCommunityRelation", "Community Relations"): [
        (
            "413-1 Operations with local community engagement, impact assessments, and development programs",
            "SocCommunityRelation413-1",
        ),
        (
            "413-2 Operations with significant actual and potential negative impacts on local communities",
            "SocCommunityRelation413-2",
        ),
    ],
    ("SocLabourManagement", "Labor Management"): [
        (
            "407-1 Operations and suppliers in which the right to freedom of association and collective bargaining may be at risk",
            "SocLabourManagement407-1",
        ),
        (
            "409-1 Operations and suppliers at significant risk for incidents of forced or compulsory labor",
            "SocLabourManagement409-1",
        ),
    ],
    ("SocEmployment", " Employment "): [
        (
            "401-2 Benefits provided to full-time employees that are not provided to temporary or part-time employees",
            "SocEmployment401-2",
        ),
        ("401-3 Parental leave", "SocEmployment401-3"),
    ],
    ("SocHumanCapitalDevelopment", "Human Capital Development"): [
        (
            "404-2 Programs for upgrading employee skills and transition assistance programs",
            "SocHumanCapitalDevelopment404-2",
        ),
        (
            "404-3 Percentage of employees receiving regular performance and career development reviews",
            "SocHumanCapitalDevelopment404-3",
        ),
        (
            "410-1 Security personnel trained in human rights policies or procedures",
            "SocHumanCapitalDevelopment410-1",
        ),
    ],
    ("SocPrivacyDataSecurity", "Privacy & Data Security"): [
        (
            "416-1 Assessment of the health and safety impacts of product and service categories",
            "SocProductSafetyQuality416-1",
        ),
        (
            "416-2 Incidents of non-compliance concerning the health and safety impacts of products and services",
            "SocProductSafetyQuality416-2",
        ),
    ],
    ("SocMarketingLabeling", "Marketing and Labeling"): [
        (
            "417-2 Incidents of non-compliance concerning product and service information and labeling",
            "SocMarketingLabeling417-2",
        ),
        (
            "417-3 Incidents of non-compliance concerning marketing communications",
            "SocMarketingLabeling417-3",
        ),
    ],
    ("SocPayEquality", "Pay equality"): [
        (
            "202-1 Ratios of standard entry level wage by gender compared to local minimum wage",
            "SocPayEquality202-1",
        )
    ],
    ("SocSupplyChainLabour", "Supply Chain Labor Standards"): [
        (
            "414-2 Negative social impacts in the supply chain and actions taken",
            "SocSupplyChainLabour414-2",
        ),
        (
            "204-1 Proportion of spending on local suppliers",
            "SocSupplyChainLabour204-1",
        ),
    ],
    ("GovEconomicImpact", "Economic impacts"): [
        ("203-2 Significant indirect economic impacts", "GovEconomicImpact203-2")
    ],
    ("GovEconomicPerformance", "Economic performance"): [
        (
            "201-2 Financial implications and other risks and opportunities due to climate change",
            "GovEconomicPerformance201-2",
        ),
        (
            "201-3 Defined benefit plan obligations and other retirement plans",
            "GovEconomicPerformance201-3",
        ),
        (
            "201-4 Financial assistance received from government",
            "GovEconomicPerformance201-4",
        ),
    ],
    ("GovCorruption", "Corruption"): [
        (
            "205-2 Communication and training about anti-corruption policies and procedures",
            "GovCorruption205-2",
        ),
        (
            "205-3 Confirmed incidents of corruption and actions taken",
            "GovCorruption205-3",
        ),
        (
            "206-1 Legal actions for anti-competitive behavior, anti-trust, and monopoly practices",
            "GovCorruption206-1",
        ),
    ],
    ("GovTaxTransparency", "Tax Transparency"): [
        (
            "207-2 Tax governance, control, and risk management",
            "GovTaxTransparency207-2",
        ),
        (
            "207-3 Stakeholder engagement and management of concerns related to tax",
            "GovTaxTransparency207-3",
        ),
        ("207-4 Country-by-country reporting", "GovTaxTransparency207-4"),
    ],
}


{
    "Packaging Material": "EnvPackagingMaterial",
    "Agriculture": "EnvAgriculture",
    "Aquaculture": "EnvAquaculture",
    "Child Labor": "SocChildLabour",
    "Product Safety & Quality": "SocProductSafetyQuality",
    "Access to Health Care": "SocHealthCare",
    "Diversity & equal oppportunity": "SocDiversityEqualOpp",
    "Non-discrimination": "SocNonDiscrimination",
    "Policy": "GovPolicy",
    "Governance": "GovGovernance",
}
