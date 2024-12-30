from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from materiality_dashboard.models import (
    MaterialityAssessment,
    AssessmentDisclosureSelection,
    Disclosure,
)
from sustainapp.models import Framework


class GetMaterialityDashboardwithDisclosures(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        client = request.user.client

        # Retrieve the materiality assessment
        try:
            query_params = {
                "client": client,
                "approach": "GRI: In accordance with",
                "status": "completed",
            }

            materiality_dashboard = MaterialityAssessment.objects.filter(
                **query_params
            ).latest("created_at")
        except MaterialityAssessment.DoesNotExist:
            materiality_dashboard = None

        # Fetch selected disclosures with topic details and related paths in one query
        selected_disclosures = (
            (
                AssessmentDisclosureSelection.objects.filter(
                    topic_selection__assessment=materiality_dashboard
                )
                .select_related(
                    "topic_selection__topic",  # Access topic details efficiently
                    "disclosure",  # Access disclosure details
                )
                .prefetch_related("disclosure__paths")
                .only(
                    "disclosure__identifier",
                    "disclosure__paths__slug",
                    "topic_selection__topic__id",
                )
            )
            if materiality_dashboard is not None
            else AssessmentDisclosureSelection.objects.none()
        )

        # Collect selected topic ids and disclosures into dictionaries to avoid redundant queries
        selected_topic_ids = set()
        material_disclosure_map = {}

        for selected_disclosure in selected_disclosures:
            topic_id = selected_disclosure.topic_selection.topic.id
            selected_topic_ids.add(topic_id)

            disclosure_identifier = selected_disclosure.disclosure.identifier
            slugs = [path.slug for path in selected_disclosure.disclosure.paths.all()]

            if topic_id not in material_disclosure_map:
                material_disclosure_map[topic_id] = []

            material_disclosure_map[topic_id].append(
                {
                    "disclosure_id": disclosure_identifier,
                    "slugs": slugs,
                    "is_material_topic": True,  # Mark as material since it's a selected disclosure
                }
            )
        framework = (
            materiality_dashboard.framework
            if materiality_dashboard is not None
            else Framework.objects.get(id=1)
        )
        # Fetch all disclosures (including both material and non-material) in one go
        all_disclosures = (
            Disclosure.objects.filter(topic__framework=framework)
            .select_related("topic")
            .prefetch_related("paths")
            .only(
                "identifier",
                "topic__id",
                "topic__esg_category",
                "topic__identifier",
                "paths__slug",
            )
        )

        # Initialize the response data structure
        response_data = {
            "environment": {},
            "social": {},
            "governance": {},
            "general": {},
        }

        # Process all disclosures and categorize them
        for disclosure in all_disclosures:
            topic = disclosure.topic
            esg_category = topic.esg_category
            topic_identifier = topic.identifier
            disclosure_identifier = disclosure.identifier

            # Get all related path slugs for the disclosure
            slugs = [path.slug for path in disclosure.paths.all()]

            # Initialize topic in the response structure if not present
            topic_dict = response_data[esg_category].setdefault(
                topic_identifier,
                {
                    "disclosures": [],  # List to hold the disclosures
                    "is_material_topic": topic.id
                    in selected_topic_ids,  # Check if material
                },
            )

            # * Create a set that checks for duplicates in disclosures
            added_disclosures = {list(d.keys())[0] for d in topic_dict["disclosures"]}
            # Append the disclosure data
            if topic.id in material_disclosure_map:
                # If the topic is already in the material_disclosure_map, add those disclosures
                for material_disclosure in material_disclosure_map[topic.id]:
                    material_id = material_disclosure["disclosure_id"]
                    if material_id not in added_disclosures:
                        topic_dict["disclosures"].append(
                            {
                                material_disclosure[
                                    "disclosure_id"
                                ]: material_disclosure["slugs"],
                                "is_material_topic": material_disclosure[
                                    "is_material_topic"
                                ],  # Material flag for selected disclosures
                            }
                        )
                        added_disclosures.add(material_id)
            else:
                # Non-material disclosure
                topic_dict["disclosures"].append(
                    {
                        disclosure_identifier: slugs,
                        "is_material_topic": False,  # Mark as non-material
                    }
                )
        # * Add Organisation, Corporate and year of materiality dashboard to the response data
        response_data["organisation"] = (
            materiality_dashboard.organization.id
            if (
                (materiality_dashboard is not None)
                and (materiality_dashboard.organization is not None)
            )
            else None
        )
        response_data["organisation_name"] = (
            materiality_dashboard.organization.name
            if (
                (materiality_dashboard is not None)
                and (materiality_dashboard.organization is not None)
            )
            else None
        )
        response_data["corporate"] = (
            materiality_dashboard.corporate.id
            if (
                (materiality_dashboard is not None)
                and (materiality_dashboard.corporate is not None)
            )
            else None
        )
        response_data["corporate_name"] = (
            materiality_dashboard.corporate.name
            if (
                (materiality_dashboard is not None)
                and (materiality_dashboard.corporate is not None)
            )
            else None
        )
        response_data["year"] = (
            materiality_dashboard.start_date.year
            if materiality_dashboard is not None
            else None
        )
        return Response(response_data)
