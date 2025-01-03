from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from materiality_dashboard.models import (
    MaterialityAssessment,
    AssessmentDisclosureSelection,
    Disclosure,
)
from sustainapp.models import Framework
from materiality_dashboard.Serializers.VerifyOrganisationAndCorporateSerializer import (
    VerifyOrganisationAndCorporateSerializer,
)


class GetMaterialityDashboardwithDisclosures(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        client = request.user.client
        serializer = VerifyOrganisationAndCorporateSerializer(
            data=request.query_params, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        organization = serializer.validated_data.get("organization")
        corporate = serializer.validated_data.get("corporate")
        start = serializer.validated_data.get("start_date")
        end = serializer.validated_data.get("end_date")

        params_given = (
            organization is not None and start is not None and end is not None
        )

        # Retrieve the materiality assessment
        try:
            if not params_given:
                query_params = {
                    "client": client,
                    "approach": "GRI: In accordance with",
                    "status": "completed",
                }
            else:
                query_params = {
                    "client": client,
                    "approach": "GRI: In accordance with",
                    "status": "completed",
                    "organization": organization,
                    "corporate": corporate,
                    "start_date__gte": start,
                    "end_date__lte": end,
                }

            materiality_dashboard = MaterialityAssessment.objects.filter(
                **query_params
            ).latest("created_at")
        except MaterialityAssessment.DoesNotExist:
            materiality_dashboard = None

        # Fetch selected disclosures with topic details and related paths in one query
        selected_disclosures = (
            AssessmentDisclosureSelection.objects.filter(
                topic_selection__assessment=materiality_dashboard
            )
            .select_related(
                "topic_selection__topic",
                "disclosure",
            )
            .prefetch_related("disclosure__paths")
            if materiality_dashboard is not None
            else AssessmentDisclosureSelection.objects.none()
        )

        # Create sets and maps for tracking selections
        selected_topic_ids = set()
        selected_disclosure_ids = set()  # Track which disclosures are selected
        material_disclosure_map = {}

        # Process selected disclosures first
        for selected_disclosure in selected_disclosures:
            topic_id = selected_disclosure.topic_selection.topic.id
            selected_topic_ids.add(topic_id)

            disclosure = selected_disclosure.disclosure
            disclosure_identifier = disclosure.identifier
            selected_disclosure_ids.add(disclosure.id)  # Track selected disclosure IDs

            if topic_id not in material_disclosure_map:
                material_disclosure_map[topic_id] = (
                    set()
                )  # Use a set to avoid duplicates

            slugs = [path.slug for path in disclosure.paths.all()]
            material_disclosure_map[topic_id].add((disclosure_identifier, tuple(slugs)))

        framework = (
            materiality_dashboard.framework
            if materiality_dashboard is not None
            else Framework.objects.get(id=1)
        )

        # Initialize response structure
        response_data = {
            "environment": {},
            "social": {},
            "governance": {},
            "general": {},
        }

        # Fetch and process all disclosures
        all_disclosures = (
            Disclosure.objects.filter(topic__framework=framework)
            .select_related("topic")
            .prefetch_related("paths")
        )

        # Track processed topics to avoid duplicates
        processed_topics = set()

        for disclosure in all_disclosures:
            topic = disclosure.topic

            # Skip if we've already processed this topic
            if topic.id in processed_topics:
                continue

            processed_topics.add(topic.id)

            esg_category = topic.esg_category
            topic_identifier = topic.identifier

            # Initialize topic in response structure
            topic_dict = response_data[esg_category].setdefault(
                topic_identifier,
                {
                    "disclosures": [],
                    "is_material_topic": topic.id in selected_topic_ids,
                },
            )

            # Get all disclosures for this topic
            topic_disclosures = Disclosure.objects.filter(topic=topic).prefetch_related(
                "paths"
            )

            if topic.id in selected_topic_ids:  # This is a material topic
                # First add the selected disclosures
                for disclosure_id, slugs in material_disclosure_map.get(
                    topic.id, set()
                ):
                    topic_dict["disclosures"].append(
                        {
                            disclosure_id: list(slugs),
                            "is_material_topic": True,
                        }
                    )

                # Then add the non-selected disclosures for this material topic
                for disc in topic_disclosures:
                    if (
                        disc.id not in selected_disclosure_ids
                    ):  # Only add if not already selected
                        slugs = [path.slug for path in disc.paths.all()]
                        topic_dict["disclosures"].append(
                            {
                                disc.identifier: slugs,
                                "is_material_topic": False,  # These are non-selected disclosures
                            }
                        )
            else:
                # For non-material topics, add all disclosures as non-material
                for disc in topic_disclosures:
                    slugs = [path.slug for path in disc.paths.all()]
                    topic_dict["disclosures"].append(
                        {
                            disc.identifier: slugs,
                            "is_material_topic": False,
                        }
                    )

        # Add additional response data
        if not params_given:
            response_data.update(
                {
                    "organisation": (
                        materiality_dashboard.organization.id
                        if materiality_dashboard and materiality_dashboard.organization
                        else None
                    ),
                    "organisation_name": (
                        materiality_dashboard.organization.name
                        if materiality_dashboard and materiality_dashboard.organization
                        else None
                    ),
                    "corporate": (
                        materiality_dashboard.corporate.id
                        if materiality_dashboard and materiality_dashboard.corporate
                        else None
                    ),
                    "corporate_name": (
                        materiality_dashboard.corporate.name
                        if materiality_dashboard and materiality_dashboard.corporate
                        else None
                    ),
                    "year": (
                        materiality_dashboard.start_date.year
                        if materiality_dashboard and materiality_dashboard.start_date
                        else None
                    ),
                }
            )

        response_data["status"] = (
            materiality_dashboard.status if materiality_dashboard else None
        )

        return Response(response_data)
