from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sustainapp.models import Report
from rest_framework.permissions import IsAuthenticated
from materiality_dashboard.models import MaterialityAssessment
from materiality_dashboard.Serializers.MaterialityAssessmentSerializer import (
    MaterialityAssessmentGetSerializer,
)
from esg_report.utils import (
    get_management_materiality_topics,
)
from esg_report.models.ScreenFifteen import ScreenFifteenModel

class SelectMaterialsTopic(APIView):
     
    """
    API View to retrieve material topics and their associated ESG data for a given report.

    This endpoint returns structured responses for environment, social, and governance topics
    associated with a report. It also includes a conclusion if available.

    Methods:
        get(request, report_id): Retrieves the materiality assessment topics and fetches
                                 the corresponding responses using predefined slugs.
                                 Also includes the 'conclusion' field from ScreenFifteenModel.
    """
     
    permission_classes = [IsAuthenticated]
    

    def get(self, request, report_id):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response({"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the relevant MaterialityAssessment
        assessment = MaterialityAssessment.objects.filter(
            client=report.client,
            organization=report.organization,
            corporate=report.corporate,
            start_date__gte=report.start_date,
            end_date__lte=report.end_date
        ).first()

        response_data = {
            "report": report.id,
            "conclusion": None,
            "environment_topic_responses": [],
            "social_topic_responses": [],
            "governance_topic_responses": []
        }

        try:
            screen_15_data = ScreenFifteenModel.objects.get(report=report)
            response_data["conclusion"] = screen_15_data.conclusion
        except ScreenFifteenModel.DoesNotExist:
            response_data["conclusion"] = None

        # Serialize and include assessment
        if assessment:
            serializer = MaterialityAssessmentGetSerializer(assessment)

            # Define the topic -> path mapping
            material_topic_mapping = {
                "GHG Emissions": "gri_collect_emission_management_material_topic",
                "Biodiversity & land use": "gri-environment-biodiversity-management-of-material-topic",
                "Air Quality": "gri-environment-air-quality-management_of_material_topic",
                "Supply chain sustainability": "gri_collect_supplier_environmental_assessment_management_material_topic",
                "Fossil Fuel": "",
                "Agriculture": "",
                "Aquaculture": "",
                "Water & effluent": "gri_collect_water_and_effluents_management_material_topic",
                "Raw Material Sourcing ": "gri_collect_materials_management_material_topic",
                "Waste Management ": "gri_collect_waste_management_material_topic",
                "Energy ": "gri_collect_energy_management_material_topic",
                "Packaging Material": "gri-environment-packaging-material-management-of-material-topic",
                "Community Relations": "",
                "Privacy & Data Security": "gri_collect_customer_privacy_management_material_topic",
                "Product Safety & Quality": "gri_collect_product_safety_management_material_topic",
                "Marketing and Labeling": "gri_collect_marketing_and_labeling_management_material_topic",
                "Pay equality": "",
                "Occupational Health &  Safety": "gri_collect_ohs_management_material_topic",
                "Labor Management": "gri_collect_labor_management_material_topic",
                "Child Labor": "gri_collect_child_labor_management_material_topic",
                " Employment ": "gri_collect_employment_management_material_topic",
                "Human Capital Development": "",
                "Access to Health Care": "",
                "Supply Chain Labor Standards": "gri_collect_supply_chain_management_material_topic",
                "Diversity & equal oppportunity": "gri_collect_diversity_equal_opportunity_management_material_topic",
                "Non-discrimination": "gri_collect_non_discrimination_management_material_topic",
                "Lobbying and Political Influence": "gri_collect_lobbying_political_influence_management_material_topic",
                "Economic impacts": "gri_collect_indirect_economic_impacts_management_material_topic",
                "Economic performance": "gri_collect_economic_performance_management_material_topic",
                "Anti-Corruption and Ethics": "gri_collect_anti_corruption_management_material_topic",
                "Tax Transparency": "gri_collect_tax_management_material_topic",
                "Economic Governance": "gri_collect_economic_governance_management_material_topic",
                "Climate Risks and Opportunities": "gri_collect_risks_and_opportunities_management_material_topic"
            }
            def normalize_topic(topic):
                    return topic.strip().replace("  ", "_").replace("& ", "_").replace(" &", "_").replace(" ", "_")
            # Helper method to collect data based on category
            def collect_responses(topic_list, category_key):
                for topic in topic_list:
                    original_topic=topic
                    slug = material_topic_mapping.get(topic, "")
                    normalized_topic = normalize_topic(original_topic)

                    if slug:
                        data = get_management_materiality_topics(report, slug)
                        response_data[category_key].append({normalized_topic: data if data else None})
                    else:
                        # Even if slug is not mapped, include null to maintain consistency
                        response_data[category_key].append({normalized_topic: None})

            collect_responses(serializer.data.get("environment_topics", []), "environment_topic_responses")
            collect_responses(serializer.data.get("social_topics", []), "social_topic_responses")
            collect_responses(serializer.data.get("governance_topics", []), "governance_topic_responses")

        return Response(response_data, status=status.HTTP_200_OK)
