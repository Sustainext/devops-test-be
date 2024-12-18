# Create your views here.
from django.conf import settings
from django.http import HttpResponseRedirect
from sustainapp.models import Organization, Corporateentity, Location
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required


def email_confirm_redirect(request, key):
    return HttpResponseRedirect(f"{settings.EMAIL_CONFIRM_REDIRECT_BASE_URL}{key}/")


def password_reset_confirm_redirect(request, uidb64, token):
    return HttpResponseRedirect(
        f"{settings.PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL}{uidb64}/{token}/"
    )


@login_required
@csrf_protect
def get_orgs_by_client(request, client_id):
    if request.method == "GET":
        orgs = Organization.objects.filter(client_id=client_id)
        data = list(orgs.values("id", "name"))
        return JsonResponse({"orgs": data})
    return JsonResponse({"error": "Invalid request method"}, status=400)


@login_required
@csrf_protect
def get_corps_by_orgs(request):
    if request.method == "GET":
        org_ids = request.GET.getlist("org_ids")
        corps = Corporateentity.objects.filter(organization_id__in=org_ids).values(
            "id", "name"
        )
        return JsonResponse({"corps": list(corps)})
    return JsonResponse({"error": "Invalid request method"}, status=400)


@login_required
@csrf_protect
def get_locs_by_corps(request):
    if request.method == "GET":
        corp_ids = request.GET.getlist("corp_ids")
        locs = Location.objects.filter(corporateentity_id__in=corp_ids).values(
            "id", "name"
        )
        return JsonResponse({"locs": list(locs)})
    return JsonResponse({"error": "Invalid request method"}, status=400)
