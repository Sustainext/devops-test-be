from django.contrib.auth import get_user_model
from openpyxl import load_workbook
from io import BytesIO
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datametric.utils.signal_utilities import set_bulk_upload_flag
from sustainapp.Views.ExcelTemplate.EmissionBulkUpload import ExcelTemplateUploadView

User = get_user_model()


class ExcelTemplateConfirmView(APIView):
    def post(self, request, *args, **kwargs):
        temp_id = request.data.get("temp_id")

        if not temp_id:
            return Response(
                {"message": "Missing temp_id."}, status=status.HTTP_400_BAD_REQUEST
            )

        cache_key = f"excel_upload:{temp_id}"
        cached_data = cache.get(cache_key)

        if not cached_data:
            return Response(
                {"message": "Session expired or invalid temp_id."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if cached_data["user_id"] != request.user.id:
            return Response(
                {"message": "Unauthorized access to temp_id."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Load workbook from cached bytes
        try:
            wb = load_workbook(BytesIO(cached_data["file_content"]), data_only=True)
            ws = wb["Template"]
        except Exception as e:
            return Response(
                {"message": f"Failed to load file: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        valid_rows, invalid_rows = ExcelTemplateUploadView().validate_data(ws, request)

        message = {}
        if len(invalid_rows) > 0:
            message["header"] = "Rows has been partially imported"
            message["body"] = (
                "Rows from the template has been partially imported into the emissions table"
            )
        elif valid_rows and len(invalid_rows) == 0:
            message["header"] = "Import Successful"
            message["body"] = (
                "Rows from the template has been imported into the emissions table"
            )
        else:
            message["header"] = "No rows has been imported"
            message["body"] = (
                "No rows from the template has been imported into the emissions table"
            )

        set_bulk_upload_flag(True)
        try:
            ExcelTemplateUploadView().save_valid_rows_to_raw_response(
                request, valid_rows
            )
        finally:
            set_bulk_upload_flag(False)

        # Cleanup
        cache.delete(cache_key)

        return Response(
            {
                "message": message,
                "valid_count": len(valid_rows),
            },
            status=status.HTTP_200_OK,
        )
