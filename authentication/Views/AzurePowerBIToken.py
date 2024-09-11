import msal
from rest_framework.response import Response
from rest_framework.views import APIView
from azureproject.settings import AZURE_POWERBI_USERNAME, AZURE_POWERBI_PASSWORD, AZURE_POWERBI_APP_ID, AZURE_POWERBI_TENANT_ID


# Optional: File cache (if you want to cache to disk)
import os
import json

class PowerBiToken(APIView):
    def get(self, request, *args, **kwargs):
        username = AZURE_POWERBI_USERNAME
        password = AZURE_POWERBI_PASSWORD
        app_id = AZURE_POWERBI_APP_ID
        tenant_id = AZURE_POWERBI_TENANT_ID

        authority_url = f'https://login.microsoftonline.com/{tenant_id}'
        scopes = ['https://analysis.windows.net/powerbi/api/.default']

        cache = msal.SerializableTokenCache()

        cache_file = 'token_cache.json'
        if os.path.exists(cache_file):
            cache.deserialize(open(cache_file, 'r').read())

        client = msal.PublicClientApplication(
            app_id,
            authority=authority_url,
            token_cache=cache  
        )

        
        accounts = client.get_accounts()
        if accounts:
            token = client.acquire_token_silent(scopes, accounts[0])
        else:
            
            token = client.acquire_token_by_username_password(
                username=username,
                password=password,
                scopes=scopes
            )

        
        if cache.has_state_changed:
            with open(cache_file, 'w') as f:
                f.write(cache.serialize())

        return Response(token)
