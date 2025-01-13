# azure_log_uploader.py
import os
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.monitor.ingestion import LogsIngestionClient

# Load environment variables from .env file
load_dotenv()


class AzureLogUploader:
    def __init__(self):
        tenant_id = os.getenv("AZURE_LOG_TENANT_ID")
        client_id = os.getenv("AZURE_LOG_CLIENT_ID")
        client_secret = os.getenv("AZURE_LOG_CLIENT_SECRET")
        endpoint = os.getenv("AZURE_LOG_LOG_ENDPOINT")

        self.credential = ClientSecretCredential(
            tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
        )
        self.client = LogsIngestionClient(endpoint=endpoint, credential=self.credential)

    def upload_logs(self, log_data):
        try:
            rule_id = os.getenv("AZURE_LOG_RULE_ID")
            stream_name = os.getenv("AZURE_LOG_STREAM_NAME")
            self.client.upload(rule_id=rule_id, stream_name=stream_name, logs=log_data)
            print("Logs sent successfully!")
        except Exception as e:
            print(f"Failed to send logs: {e}")


# Example usage (this part can be in another module)
if __name__ == "__main__":
    uploader = AzureLogUploader()

    # Define log data
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

    rule_id = os.getenv("AZURE_LOG_RULE_ID")
    stream_name = os.getenv("AZURE_LOG_STREAM_NAME")

    # Upload logs
    uploader.upload_logs(rule_id, stream_name, log_data)
