# loguploader/views.py
from django.http import JsonResponse
from rest_framework.views import APIView
from azurelogs.azure_log_uploader import (
    AzureLogUploader,
)


class LogUploadView(APIView):
    def post(self, request):
        print('loguploader api hit')
        try:
            # Extract data from the request
            event_type = request.data.get("event_type")
            time_generated = request.data.get("time_generated")
            event_details = request.data.get("event_details")
            action_type = request.data.get("action_type")
            status = request.data.get("status")
            user_email = request.data.get("user_email")
            user_role = request.data.get("user_role")
            logs = request.data.get("logs")
            organization = request.data.get("organization")
            ip_address = request.data.get("ip_address")

            # Prepare log data for uploading
            log_data = [
                {
                    "EventType": event_type,
                    "TimeGenerated": time_generated,
                    "EventDetails": event_details,
                    "Action": action_type,
                    "Status": status,
                    "UserEmail": user_email,
                    "UserRole": user_role,
                    "Logs": logs,
                    "Organization": organization,
                    "IPAddress": ip_address,
                }
            ]

            # Initialize AzureLogUploader and upload logs
            uploader = AzureLogUploader()
            uploader.upload_logs(log_data)

            return JsonResponse({"message": "Logs uploaded successfully!"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
