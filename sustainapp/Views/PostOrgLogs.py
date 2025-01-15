# loguploader/views.py
from django.http import JsonResponse
from django.views import View
from azurelogs.azure_log_uploader import AzureLogUploader  # Import your AzureLogUploader class
import urllib.parse

class LogUploadView(View):
    def post(self, request):
        try:
            # Decode and parse the form-encoded data from the request body
            body_unicode = request.body.decode('utf-8')  # Decode bytes to string
            body_data = urllib.parse.parse_qs(body_unicode)  # Parse query string
            
            # Extract individual fields from parsed data
            event_type = body_data.get('EventType', [None])[0]
            time_generated = body_data.get('TimeGenerated', [None])[0]
            event_details = body_data.get('EventDetails', [None])[0]
            action_type = body_data.get('Action', [None])[0]
            status = body_data.get('Status', [None])[0]
            user_email = body_data.get('UserEmail', [None])[0]
            user_role = body_data.get('UserRole', [None])[0]
            logs = body_data.get('Logs', [None])[0]
            organization = body_data.get('Organization', [None])[0]
            ip_address = body_data.get('IPAddress', [None])[0]

            # Prepare log data for uploading
            log_data = {
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

            # Initialize AzureLogUploader and upload logs
            uploader = AzureLogUploader()
            uploader.upload_logs(log_data)

            return JsonResponse({"message": "Logs uploaded successfully!"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
