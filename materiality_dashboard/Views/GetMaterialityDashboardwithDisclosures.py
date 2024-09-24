from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from materiality_dashboard.models import (
    MaterialityAssessment,
    AssessmentDisclosureSelection,
    Disclosure,
)
from materiality_dashboard.Serializers.VerifyOrganisationAndCorporateSerializer import (
    VerifyOrganisationAndCorporateSerializer,
)


class GetMaterialityDashboardwithDisclosures(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Validate the query parameters
        serializer = VerifyOrganisationAndCorporateSerializer(
            data=request.query_params, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        organization = serializer.validated_data["organization"]
        corporate = serializer.validated_data.get("corporate")
        client = request.user.client

        # Retrieve the materiality assessment
        try:
            query_params = {
                "client": client,
                "organization": organization,
                "status": "in_progress",
            }
            if corporate:
                query_params["corporate"] = corporate

            materiality_dashboard = MaterialityAssessment.objects.get(**query_params)
        except MaterialityAssessment.DoesNotExist:
            return Response(
                {
                    "message": "Materiality Assessment not found for the given Organization and Corporate"
                },
                status=400,
            )

        # Fetch all disclosures (both material and non-material) in a single query
        all_disclosures = (
            Disclosure.objects.filter(topic__framework=materiality_dashboard.framework)
            .select_related("topic")  # Fetch related topic in one query
            .prefetch_related("paths")  # Fetch related paths in one query
        )

        # Fetch selected disclosures with related data
        selected_disclosures = (
            AssessmentDisclosureSelection.objects.filter(
                topic_selection__assessment=materiality_dashboard
            )
            .select_related(
                "topic_selection__topic",  # Access topic details
                "disclosure",  # Access disclosure details
            )
            .prefetch_related("disclosure__paths")  # Prefetch paths for disclosures
        )

        # Create a set of selected topic IDs for quick lookup
        selected_topic_ids = set(
            selected_disclosure.topic_selection.topic.id
            for selected_disclosure in selected_disclosures
        )

        # Initialize the response data structure
        response_data = {"environment": {}, "social": {}, "governance": {}}

        # Combine selected and non-selected disclosures in one loop
        for disclosure in all_disclosures:
            topic = disclosure.topic
            esg_category = topic.esg_category
            topic_identifier = topic.identifier
            disclosure_identifier = disclosure.identifier

            # Get all related path slugs for the disclosure
            slugs = [
                slug for slug in disclosure.paths.all().values_list("slug", flat=True)
            ]

            # Initialize topic in the response structure if not present
            topic_dict = response_data[esg_category].setdefault(
                topic_identifier,
                {
                    "disclosures": [],  # List to hold the disclosures
                    "is_material_topic": topic.id
                    in selected_topic_ids,  # Check if material
                },
            )

            # Append the disclosure data
            topic_dict["disclosures"].append({disclosure_identifier: slugs})

        return Response(response_data)
