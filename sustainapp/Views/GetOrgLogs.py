import os
from datetime import timedelta
from rest_framework.response import Response
from rest_framework.views import APIView
from azure.monitor.query import LogsQueryClient
from azure.identity import ClientSecretCredential
from rest_framework.permissions import IsAuthenticated


class AzureMonitorQueryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Retrieve Azure credentials from environment variables
        tenant_id = os.getenv("AZURE_LOG_TENANT_ID")
        client_id = os.getenv("AZURE_LOG_CLIENT_ID")
        client_secret = os.getenv("AZURE_LOG_CLIENT_SECRET")
        workspace_id = os.getenv("AZURE_LOG_WORKSPACE_ID")

        # Check if any of the required credentials are missing
        if not all([tenant_id, client_id, client_secret, workspace_id]):
            return Response(
                {"error": "Missing environment variables for Azure credentials."},
                status=400,
            )

        # Set up credentials
        credential = ClientSecretCredential(
            tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
        )

        # Create the LogsQueryClient
        logs_query_client = LogsQueryClient(credential)

        # Example of a valid KQL query
        query = """
        custom_log_CL_CL
        | where TimeGenerated >= ago(1d)
        | project TimeGenerated, EventType, EventDetails, Action, Status, UserEmail, UserRole
        | order by TimeGenerated desc
        """

        try:
            response = logs_query_client.query_workspace(
                workspace_id, query, timespan=timedelta(days=1)
            )

            results = []
            # Process the results
            for table in response.tables:
                for row in table.rows:
                    row_dict = dict(zip(table.columns, row))
                    results.append(row_dict)

            return Response({"results": results}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
