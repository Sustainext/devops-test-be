from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from sustainapp.models import (
    Framework,
    Regulation,
    Target,
    Sdg,
    Certification,
    Rating,
    Organization,
    Userorg,
)
from sustainapp.serializers import (
    FrameworkSerializer,
    RegulationSerializer,
    TargetSerializer,
    SdgSerializer,
    CertificationSerializer,
    RatingSerializer,
)
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User, Group
from django.http import JsonResponse


class FrameworkReadOnlyModelViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Framework.objects.all()
    serializer_class = FrameworkSerializer


class RegulationReadOnlyModelViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Regulation.objects.all()
    serializer_class = RegulationSerializer


class TargetReadOnlyModelViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Target.objects.all()
    serializer_class = TargetSerializer


class SdgReadOnlyModelViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Sdg.objects.all()
    serializer_class = SdgSerializer


class CertificationReadOnlyModelViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer


class RatingReadOnlyModelViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer


def get_preference_queryset(preference):
    """
    Returns a queryset for the specified preference type.

    Args:
        preference (str): The type of preference to retrieve, such as "framework", "regulation", "target", "sdg", "certification", or "rating".

    Returns:
        A queryset of the specified preference type, or None if the preference type is not found.
    """
    preferences = {
        "framework": Framework.objects.all(),
        "regulation": Regulation.objects.all(),
        "target": Target.objects.all(),
        "sdg": Sdg.objects.all(),
        "certification": Certification.objects.all(),
        "rating": Rating.objects.all(),
    }
    return preferences.get(preference, None)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def TypeOfPreference(request):
    try:
        user = request.user
        preference = request.GET.get("preference")

        queryset = get_preference_queryset(preference)

        if queryset is None:
            return JsonResponse(
                {"error": "Invalid preference type"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user_org = (
                Userorg.objects.filter(client_id=request.client.id)
                .filter(user=user)
                .first()
            )
            if user_org is None:
                raise Userorg.DoesNotExist
        except Userorg.DoesNotExist:
            return JsonResponse(
                {"error": "User not linked to any Organization"},
                status=status.HTTP_404_NOT_FOUND,
            )

        org = user_org.organization

        if preference == "sdg":
            linked_prefrerence = org.sdg.all()
            linked_prefrerence_ids = [sdg.id for sdg in linked_prefrerence]
        elif preference == "certification":
            linked_prefrerence = org.certification.all()
            linked_prefrerence_ids = [
                certification.id for certification in linked_prefrerence
            ]
        elif preference == "rating":
            linked_prefrerence = org.rating.all()
            linked_prefrerence_ids = [rating.id for rating in linked_prefrerence]
        elif preference == "framework":
            linked_prefrerence = org.framework.all()
            linked_prefrerence_ids = [framework.id for framework in linked_prefrerence]
        elif preference == "regulation":
            linked_prefrerence = org.regulation.all()
            linked_prefrerence_ids = [
                regulation.id for regulation in linked_prefrerence
            ]
        else:
            linked_prefrerence = org.target.all()
            linked_prefrerence_ids = [target.id for target in linked_prefrerence]

        if linked_prefrerence_ids == []:
            linked_prefrerence_ids = None

        data = []
        for obj in queryset:
            data.append(
                {
                    "id": obj.id,
                    "name": obj.name,
                    "Image": obj.Image.url if obj.Image else None,
                }
            )

        response_data = {
            "username": user.username,
            "preference": preference,
            "data": data,
            "selected_ids": linked_prefrerence_ids,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return JsonResponse(
            {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
def OrgPreference(request):

    permission_classes = [IsAuthenticated]
    try:
        user = request.user
        if not user.is_authenticated:
            return JsonResponse(
                {"error": "Invalid or missing authentication token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            user_org = (
                Userorg.objects.filter(client_id=request.client.id)
                .filter(user=user)
                .first()
            )
            if user_org is None:
                raise Userorg.DoesNotExist
        except Userorg.DoesNotExist:
            return JsonResponse(
                {"error": "User not linked to any Organization"},
                status=status.HTTP_404_NOT_FOUND,
            )

        org = user_org.organization
        if org is None:
            return JsonResponse(
                {"error": "Organization not found"}, status=status.HTTP_404_NOT_FOUND
            )
        org_data = Organization.objects.filter(id=org.id).first()
        if org_data:
            # Fetching related data for organization
            sdgs = []
            for sdg in org_data.sdg.all():
                sdgs.append(
                    {"name": sdg.name, "Image": sdg.Image.url if sdg.Image else None}
                )
            if sdgs == []:
                sdgs = None
            ratings = []
            for rating in org_data.rating.all():
                ratings.append(
                    {
                        "name": rating.name,
                        "Image": rating.Image.url if rating.Image else None,
                    }
                )
            if ratings == []:
                ratings = None
            targets = []
            for target in org_data.target.all():
                targets.append(
                    {
                        "name": target.name,
                        "Image": target.Image.url if target.Image else None,
                    }
                )
            if targets == []:
                targets = None
            certifications = []
            for certification in org_data.certification.all():
                certifications.append(
                    {
                        "name": certification.name,
                        "Image": (
                            certification.Image.url if certification.Image else None
                        ),
                    }
                )
            if certifications == []:
                certifications = None
            frameworks = []
            for framework in org_data.framework.all():
                frameworks.append(
                    {
                        "name": framework.name,
                        "Image": framework.Image.url if framework.Image else None,
                    }
                )
            if frameworks == []:
                frameworks = None
            regulations = []
            for regulation in org_data.regulation.all():
                regulations.append(
                    {
                        "name": regulation.name,
                        "Image": regulation.Image.url if regulation.Image else None,
                    }
                )
            if regulations == []:
                regulations = None
        org_data_dict = {
            "id": org_data.id,
            "name": org_data.name,
            "sdg": sdgs,
            "rating": ratings,
            "target": targets,
            "certification": certifications,
            "framework": frameworks,
            "regulation": regulations,
        }

        return Response({"org_data": org_data_dict}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return JsonResponse(
            {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
        )


MODEL_MAP = {
    "framework": Framework,
    "regulation": Regulation,
    "target": Target,
    "sdg": Sdg,
    "certification": Certification,
    "rating": Rating,
}


@api_view(["PUT"])
def UpdatePreference(request):

    permission_classes = [IsAuthenticated]
    try:
        user = request.user
        if not user.is_authenticated:
            return JsonResponse(
                {"error": "Invalid or missing authentication token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        preference = request.data.get("preference")
        preference_ids = request.data.get("preference_ids", [])

        user_org = (
            Userorg.objects.filter(client_id=request.client.id)
            .filter(user=user)
            .first()
        )
        if user_org is None:
            return JsonResponse(
                {"error": "User not linked to any Organization"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        org = user_org.organization

        queryset_model = MODEL_MAP.get(preference)
        if not queryset_model:
            return JsonResponse(
                {"error": "Invalid preference type"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Fetch the objects corresponding to the provided IDs
        objects_to_link = queryset_model.objects.filter(id__in=preference_ids)

        try:
            getattr(org, preference).set(objects_to_link)
            org.save()
            return Response(
                {
                    "message": f"{preference} preferences updated successfully for organization"
                },
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return JsonResponse(
            {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
        )
