from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from collections import defaultdict
from materiality_dashboard.models import (
    MaterialityAssessment,
    AssessmentDisclosureSelection,
    MaterialTopic,
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

        # Fetch selected disclosures with related data to minimize queries
        selected_disclosures = (
            AssessmentDisclosureSelection.objects.filter(
                topic_selection__assessment=materiality_dashboard
            )
            .select_related(
                "topic_selection__topic",  # For accessing topic details
                "disclosure",  # For accessing disclosure details
            )
            .prefetch_related(
                "disclosure__path_set",  # For accessing related paths
            )
        )

        # Initialize the response data structure
        response_data = {"environment": {}, "social": {}, "governance": {}}
        selected_material_topics = []
        # Process the disclosures in a single loop
        for selected_disclosure in selected_disclosures:
            topic_selection = selected_disclosure.topic_selection
            topic = topic_selection.topic
            disclosure = selected_disclosure.disclosure
            selected_material_topics.append(topic.id)
            esg_category = topic.esg_category
            topic_identifier = topic.identifier
            disclosure_identifier = disclosure.identifier

            # Get all related path slugs
            slugs = [path.slug for path in disclosure.path_set.all().only("slug")]

            topic_dict = response_data[esg_category].setdefault(
                topic_identifier,
                {
                    "disclosures": [],  # List to hold the disclosures
                    "is_material_topic": True,
                },
            )

            # Append the disclosure data
            topic_dict["disclosures"].append({disclosure_identifier: slugs})

        disclosures = (
            Disclosure.objects.filter(topic__framework=materiality_dashboard.framework)
            .exclude(topic__id__in=selected_material_topics)
            .prefetch_related("path_set")
        )

        for disclosure_object in disclosures:
            topic = disclosure_object.topic
            disclosure = disclosure_object
            esg_category = topic.esg_category
            topic_identifier = topic.identifier
            disclosure_identifier = disclosure.identifier

            # Get all related path slugs
            slugs = [path.slug for path in disclosure.path_set.all().only("slug")]

            topic_dict = response_data[esg_category].setdefault(
                topic_identifier,
                {
                    "disclosures": [],  # List to hold the disclosures
                    "is_material_topic": False,
                },
            )

            # Append the disclosure data
            topic_dict["disclosures"].append({disclosure_identifier: slugs})
        return Response(response_data)
