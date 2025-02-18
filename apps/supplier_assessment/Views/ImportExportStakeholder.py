# core/views.py
import csv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from apps.supplier_assessment.models.StakeHolder import StakeHolder
from django.http import HttpResponse
from apps.supplier_assessment.Serializer.StakeHolderSerializer import (
    StakeHolderCSVSerializer,
)
from rest_framework.permissions import IsAuthenticated
from apps.supplier_assessment.Serializer.StakeHolderGroupSerializer import (
    CheckStakeHolderGroupSerializer,
)
from io import StringIO
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import datetime

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

class StakeholderUploadAPIView(APIView):
    """
    This endpoint receives a CSV file containing columns:
      - 'Stakeholder Name' (required)
      - 'Stakeholder Email' (required)
      - 'Country' (optional)
      - 'City' (optional)
      - 'State' (optional)
      - 'SPOC Name' (optional)

    Rows missing Stakeholder Name or Stakeholder Email, or with an invalid email,
    are collected into a separate CSV file that is uploaded to Azure Data Storage.
    Valid rows are created in bulk.
    """

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # 1. Validate CSV file presence
        csv_file_serializer = StakeHolderCSVSerializer(data=request.data)
        if not csv_file_serializer.is_valid():
            return Response(
                csv_file_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        csv_file = csv_file_serializer.validated_data["csv_file"]

        # 2. Validate StakeHolderGroup presence
        check_stakeholder_group_serializer = CheckStakeHolderGroupSerializer(
            data=request.data, context={"request": request}
        )
        if not check_stakeholder_group_serializer.is_valid():
            return Response(
                check_stakeholder_group_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        group = check_stakeholder_group_serializer.validated_data["group"]

        # 3. Parse the CSV file
        try:
            decoded_file = csv_file.read().decode("utf-8").splitlines()
        except Exception as e:
            return Response(
                {"detail": f"Error decoding CSV file: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reader = csv.DictReader(decoded_file)

        # We expect at least these columns
        expected_columns = {
            "Stakeholder Name",
            "Stakeholder Email",
            "Country",
            "City",
            "State",
            "SPOC Name",
        }
        missing_columns = [
            col for col in expected_columns if col not in reader.fieldnames
        ]
        if missing_columns:
            return Response(
                {
                    "detail": (
                        "CSV must contain the columns "
                        f"{list(expected_columns)}. Missing: {missing_columns}"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Lists to track valid and invalid rows
        valid_stakeholders = []
        incomplete_rows = []
        created_ids = []

        row_number = 2  # row 1 is the CSV header

        # 4. Validate each row
        for row in reader:
            stakeholder_name = row.get("Stakeholder Name", "").strip()
            stakeholder_email = row.get("Stakeholder Email", "").strip()
            country = row.get("Country", "").strip()
            city = row.get("City", "").strip()
            state = row.get("State", "").strip()
            spoc_name = row.get("SPOC Name", "").strip()

            # Check mandatory fields
            if not stakeholder_name:
                row["Reason"] = "Stakeholder Name not present"
                incomplete_rows.append(row)
                row_number += 1
                continue

            if not stakeholder_email:
                row["Reason"] = "Stakeholder Email not present"
                incomplete_rows.append(row)
                row_number += 1
                continue

            # Validate email format
            try:
                validate_email(stakeholder_email)
            except ValidationError:
                row["Reason"] = "Stakeholder Email not in correct format"
                incomplete_rows.append(row)
                row_number += 1
                continue

            # All mandatory checks pass -> create StakeHolder instance
            stakeholder_obj = StakeHolder(
                name=stakeholder_name,
                email=stakeholder_email,
                country=country,
                city=city,
                state=state,
                poc=spoc_name,  # 'SPOC Name' maps to 'poc'
                group=group,
            )
            valid_stakeholders.append(stakeholder_obj)
            row_number += 1

        # 5. Bulk create valid stakeholders in one query
        created_objs = StakeHolder.objects.bulk_create(valid_stakeholders)
        for obj in created_objs:
            created_ids.append(str(obj.id))

        # 6. If we have incomplete rows, generate a CSV and upload it to Azure
        incomplete_file_url = None
        if incomplete_rows:
            output = StringIO()
            fieldnames = [
                "Stakeholder Name",
                "Stakeholder Email",
                "Country",
                "City",
                "State",
                "SPOC Name",
                "Reason",
            ]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for bad_row in incomplete_rows:
                writer.writerow(bad_row)
            csv_content = output.getvalue()

            # Generate a unique filename using current timestamp
            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"incomplete_stakeholders_{now}.csv"

            # Create a ContentFile and save it using the default storage (Azure)
            content_file = ContentFile(csv_content.encode("utf-8"))
            file_path = default_storage.save(filename, content_file)
            incomplete_file_url = default_storage.url(file_path)

        # 7. Construct the response
        response_data = {
            "detail": "CSV processed successfully (partial acceptance).",
            "total_valid_rows": len(created_ids),
            "total_incomplete_rows": len(incomplete_rows),
        }
        if incomplete_file_url:
            response_data["incomplete_file_url"] = incomplete_file_url

        return Response(response_data, status=status.HTTP_200_OK)


class StakeholderExportAPIView(APIView):
    """
    Exports StakeHolder objects as a CSV:
      - 'Stakeholder Name'
      - 'Stakeholder Email'
      - 'SPOC Name'
    Filters by 'group' provided by the user, validated the same
    way your upload API does.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # 1) Validate the incoming group param via the same serializer
        serializer = CheckStakeHolderGroupSerializer(
            data=request.query_params,  # or request.data if you prefer
            context={"request": request},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 2) Extract the validated group
        group = serializer.validated_data["group"]

        # 3) Filter the StakeHolder objects by group
        stakeholders_qs = StakeHolder.objects.filter(group=group)

        # 4) Create the CSV response
        #    We'll return an HttpResponse so the browser can download it.
        response = HttpResponse(content_type="application/octet-stream")
        response["Content-Disposition"] = 'attachment; filename="stakeholders.csv"'

        writer = csv.writer(response)
        # Write the CSV header in the same format as your template
        writer.writerow(["Stakeholder Name", "Stakeholder Email", "SPOC Name"])

        # Write each stakeholder row
        for stakeholder in stakeholders_qs:
            writer.writerow([stakeholder.name, stakeholder.email, stakeholder.poc])

        return response
