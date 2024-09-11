import requests
import msal
from rest_framework.response import Response
from rest_framework.views import APIView

class PowerBiToken(APIView):
    def get(self, request, *args, **kwargs):
        username= "datascience@sustainext.ai"
        password= "MasterSustainer@ds97"
        
        app_id = '56e27fa8-92e1-4f05-ac3a-02f0d61f4c34'
        tenant_id = 'b0f8e84c-e4a8-4799-81b0-df150064037d'

        authority_url = 'https://login.microsoftonline.com/' + tenant_id
        scopes =['https://analysis.windows.net/powerbi/api/.default']

        #Step1 Generate PowerBi Access Token
        client = msal.PublicClientApplication(app_id, authority=authority_url)
        token = client.acquire_token_by_username_password(username=username,password=password,scopes=scopes)
        print(token)
        return Response(token)

