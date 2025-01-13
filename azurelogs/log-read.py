from azure.monitor.query import LogsQueryClient
from azure.identity import ClientSecretCredential
from datetime import timedelta

# Set up credentials
credential = ClientSecretCredential(
    tenant_id="b0f8e84c-e4a8-4799-81b0-df150064037d",  # Replace with your Azure AD tenant ID
    client_id="f5546f6e-2c13-4090-8c2f-d42cda5751a6",  # Replace with your Azure AD application (client) ID
    client_secret="Mtr8Q~MhdQRxs0dMv~1vQKODUsE5lY8JFFgyearP",
)

# Create the LogsQueryClient
logs_query_client = LogsQueryClient(credential)

workspace_id = "c909637a-b389-4661-af56-e000a6a3bbc6"

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

    # Process the results
    for table in response.tables:
        for row in table.rows:
            print(row)

except Exception as e:
    print(f"Error: {str(e)}")
