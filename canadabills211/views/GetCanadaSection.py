from sustainapp.models import Corporateentity
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


class GetCanadaSection(APIView):
    def validate_org(self, request):
        orgs = request.user.orgs.all()
        corps = request.user.corps.all()
        enable_section = False
        org_list = []
        corp_list = []

        for org in orgs:
            if org.countryoperation == "CA":
                org_list.append({"id": org.id, "name": org.name})
            else:
                continue

        for corp in corps:
            if corp.Country == "CA":
                corp_list.append({"id": corp.id, "name": corp.name})
            else:
                continue

        if org_list:
            enable_section = True
        else:
            enable_section = False

        return {
            "enable_section": enable_section,
            "org_list": org_list,
            "corp_list": corp_list,
        }

    def get(self, request, *args, **kwargs):
        response = self.validate_org(request)
        return Response(response, status=status.HTTP_200_OK)


class CorporateListCanadaData(APIView):
    def get(self, request, *args, **kwargs):
        org_id = self.request.query_params.get("org_id")
        corp_list = []
        corps = Corporateentity.objects.filter(organization_id=org_id)
        for corp in corps:
            if corp.Country == "CA":
                corp_list.append({"id": corp.id, "name": corp.name})
            else:
                continue
        return Response(corp_list, status=status.HTTP_200_OK)
