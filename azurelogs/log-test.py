import os
from azure.identity import ClientSecretCredential
from azure.monitor.ingestion import LogsIngestionClient

# Define your Azure AD application credentials directly in the script
tenant_id = (
    "b0f8e84c-e4a8-4799-81b0-df150064037d"  # Replace with your Azure AD tenant ID
)
client_id = "f5546f6e-2c13-4090-8c2f-d42cda5751a6"  # Replace with your Azure AD application (client) ID
client_secret = (
    "Mtr8Q~MhdQRxs0dMv~1vQKODUsE5lY8JFFgyearP"  # Replace with your client secret
)

# Set up the ClientSecretCredential
credential = ClientSecretCredential(
    tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
)

# Define the endpoint for your Data Collection Endpoint (DCE)
endpoint = "https://custom-log-endpoint-in-fo2z.centralindia-1.ingest.monitor.azure.com"

# Create the LogsIngestionClient with the endpoint and credential
client = LogsIngestionClient(endpoint=endpoint, credential=credential)

# Define the log data you want to send
log_data = [
    {
        "TimeGenerated": "2024-01-06T12:05:00Z",
        "EventType": "Password Change",
        "EventDetails": "User changed password successfully",
        "Action": "Change Password",
        "Status": "Success",
        "UserEmail": "user1@example.com",
        "UserRole": "Admin",
    },
]

rule_id = "dcr-dbc01e4741364cb3a9a45aba30c85e94"
stream_name = "Custom-custom_log_CL_CL"  # Replace with your actual stream name

# Send log data to Azure Monitor
client.upload(
    rule_id=rule_id,
    stream_name=stream_name,
    logs=log_data,
    # log_type="CustomLogType"  # You can define your custom log type here
)

print("Logs sent successfully!")
