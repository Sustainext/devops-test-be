from sustainapp.models import Corporateentity
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


class GetCanadaSection(APIView):
    """
    Get Canada Section based on orgs
    Validate orgs and return enable_section and org_list
    """

    def validate_org(self, request):
        orgs = request.user.orgs.all().filter(country="CA")
        enable_section = False
        org_list = list(orgs.values("id", "name"))

        if org_list:
            enable_section = True
        else:
            enable_section = False

        return {
            "enable_section": enable_section,
            "org_list": org_list,
        }

    def get(self, request, *args, **kwargs):
        response = self.validate_org(request)
        return Response(response, status=status.HTTP_200_OK)


class CorporateListCanadaData(APIView):
    """Fetches Coporated based on organization id that has country as canada"""

    def get(self, request, *args, **kwargs):
        org_id = self.request.query_params.get("org_id")
        corp_list = []
        corps = Corporateentity.objects.filter(organization_id=org_id)
        for corp in corps:
            if corp.country == "CA":
                corp_list.append({"id": corp.id, "name": corp.name})
            else:
                continue
        return Response(corp_list, status=status.HTTP_200_OK)
