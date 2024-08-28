from django.utils.deprecation import MiddlewareMixin
from datametric.models import RawResponse,Path
from urllib.parse import urlparse, parse_qs
from sustainapp.models import Organization, Corporateentity
from rest_framework.response import Response
from rest_framework import status

class PathSlugMiddleware(MiddlewareMixin):
    def get_sector_data(self, request, organization_id,corporate_id):
        organization_id = organization_id
        corporate_id = corporate_id
        if corporate_id:
            corporate_entity = Corporateentity.objects.filter(id=corporate_id)
            sector_subindustry_data = []
            for corporate_entity in corporate_entity:
                sector_subindustry_data.append({
                    'corporate_name': corporate_entity.name,
                    'Sector': corporate_entity.sector,
                    'Sub_industry': corporate_entity.subindustry
                })
            return sector_subindustry_data
        elif organization_id:
            organization = Organization.objects.filter(id=organization_id)
            corporate_entities = Corporateentity.objects.filter(organization_id=organization_id)
            sector_subindustry_data = []
            for org in organization:
                sector_subindustry_data.append({
                    'organization_name':org.name,
                    'Sector': org.sector,
                    'Sub_industry': org.subindustry
                })
            for corporate_entity in corporate_entities:
                sector_subindustry_data.append({
                    'corporate_name': corporate_entity.name,
                    'Sector': corporate_entity.sector,
                    'Sub_industry': corporate_entity.subindustry
                })
            return sector_subindustry_data
        
    def process_view(self, request, view_func, view_args, view_kwargs):
        print(f"User: {request.user}, Authenticated: {request.user.is_authenticated}")
        
        if request.method == 'GET' and request.path == '/datametric/get-fieldgroups':
            query_params = parse_qs(urlparse(request.get_full_path()).query)
            path_name = query_params.get('path_slug', [None])[0]


            if path_name == 'gri-general-business_details-organisation-2-6a':
                # Extract the relevant data from the request
                organization = request.GET.get('organisation')
                corporate = request.GET.get('corporate')
                year = request.GET.get('year')
                user = request.user
                client = user.client_id
                data = self.get_sector_data(request, organization, corporate)
                
                # Fetch the Path instance
                path_instance = Path.objects.get(slug=path_name)

                # Check if a RawResponse with the same filter criteria already exists
                if not RawResponse.objects.filter(
                    organization_id=organization,
                    corporate_id=corporate,
                    year=year,
                    path=path_instance,
                    user=user,
                    client_id=client
                ).exists():
                    # If it doesn't exist, create a new RawResponse entry
                    RawResponse.objects.create(
                        organization_id=organization,
                        corporate_id=corporate,
                        year=year,
                        path=path_instance,
                        user=user,
                        client_id=client,
                        data=data
                    )
                    print("PathSlugMiddleware: RawResponse created")
                else:
                    print("PathSlugMiddleware: RawResponse already exists")

        return None