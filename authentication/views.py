from django.shortcuts import render

# Create your views here.
from django.conf import settings
from django.http import HttpResponseRedirect
from sustainapp.models import Organization, Corporateentity, Location
from django.http import JsonResponse
from authentication.Permissions.isSuperuserAndClientAdmin import (
    superuser_and_client_admin_required,
)
from rest_framework.decorators import api_view, permission_classes


def email_confirm_redirect(request, key):
    return HttpResponseRedirect(f"{settings.EMAIL_CONFIRM_REDIRECT_BASE_URL}{key}/")


def password_reset_confirm_redirect(request, uidb64, token):
    return HttpResponseRedirect(
        f"{settings.PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL}{uidb64}/{token}/"
    )


@api_view(["GET"])
@permission_classes([superuser_and_client_admin_required])
def get_orgs_by_client(request, client_id):
    orgs = Organization.objects.filter(client_id=client_id)
    data = list(orgs.values("id", "name"))
    return JsonResponse({"orgs": data})


@api_view(["GET"])
@permission_classes([superuser_and_client_admin_required])
def get_corps_by_orgs(request):
    org_ids = request.GET.getlist("org_ids")
    corps = Corporateentity.objects.filter(organization_id__in=org_ids).values(
        "id", "name"
    )
    return JsonResponse({"corps": list(corps)})


@api_view(["GET"])
@permission_classes([superuser_and_client_admin_required])
def get_locs_by_corps(request):
    corp_ids = request.GET.getlist("corp_ids")
    locs = Location.objects.filter(corporateentity_id__in=corp_ids).values("id", "name")
    return JsonResponse({"locs": list(locs)})
