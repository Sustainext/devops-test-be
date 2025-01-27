import os
from rest_framework.response import Response
from rest_framework.views import APIView
from azure.monitor.query import LogsQueryClient
from azure.identity import ClientSecretCredential
from rest_framework.permissions import IsAuthenticated
from datetime import datetime


class AzureMonitorQueryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.query_params.get("from_date")
        end_date = request.query_params.get("to_date")
        if not start_date or not end_date:
            return Response(
                {"error": "Both from date and to date are required."}, status=400
            )
        # Retrieve Azure credentials from environment variables
        tenant_id = os.getenv("AZURE_LOG_TENANT_ID")
        client_id = os.getenv("AZURE_LOG_CLIENT_ID")
        client_secret = os.getenv("AZURE_LOG_CLIENT_SECRET")
        workspace_id = os.getenv("AZURE_LOG_WORKSPACE_ID")
        stream_name = os.getenv("AZURE_LOG_STREAM_NAME")
        table_name = stream_name.split("-")[1] if "-" in stream_name else None
        exclude_email = (
            os.getenv("EXCLUDE_SUSTAINEXT_EMAIL_LOGS", "False").lower() == "true"
        )
        print(exclude_email)

        # Check if any of the required credentials are missing
        if not all([tenant_id, client_id, client_secret, workspace_id]):
            return Response(
                {"error": "Missing environment variables for Azure credentials."},
                status=400,
            )
        if table_name is None:
            return Response(
                {
                    "error": "Invalid stream name."  # Expected format: 'stream-<table_name>'
                },
                status=400,
            )

        # Set up credentials
        credential = ClientSecretCredential(
            tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
        )

        # Create the LogsQueryClient
        logs_query_client = LogsQueryClient(credential)

        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

        start_datetime_start_of_day = start_datetime.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_datetime_end_of_day = end_datetime.replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        start_datetime_iso = start_datetime_start_of_day.isoformat()
        end_datetime_iso = end_datetime_end_of_day.isoformat()

        query = f"""
        {table_name}
        | where TimeGenerated >= datetime("{start_datetime_iso}") and TimeGenerated <= datetime("{end_datetime_iso}")
        """
        if exclude_email:
            query += """
            | where not(UserEmail endswith "@sustainext.ai")
            """
        query += """
        | project TimeGenerated, EventType, EventDetails, Action, Status, UserEmail, UserRole, Logs, Organization, IPAddress
        | order by TimeGenerated desc
        | take 200
        """
        try:
            response = logs_query_client.query_workspace(
                workspace_id, query, timespan=(end_datetime - start_datetime)
            )

            results = []
            print(response)
            # Process the results
            for table in response.tables:
                for row in table.rows:
                    row_dict = dict(zip(table.columns, row))
                    results.append(row_dict)

            return Response({"results": results}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
