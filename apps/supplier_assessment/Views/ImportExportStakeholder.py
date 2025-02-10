# core/views.py
import csv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from apps.supplier_assessment.models.StakeHolder import StakeHolder
from django.http import HttpResponse
from apps.supplier_assessment.Serializer.StakeHolderSerializer import (
    StakeHolderSerializer,
)
from apps.supplier_assessment.Serializer.StakeHolderSerializer import (
    StakeHolderCSVSerializer,
)
from rest_framework.permissions import IsAuthenticated
from apps.supplier_assessment.Serializer.StakeHolderGroupSerializer import (
    CheckStakeHolderGroupSerializer,
)


class StakeholderUploadAPIView(APIView):
    """
    This endpoint receives a CSV file containing rows with:
      - 'Stakeholder Name'
      - 'Stakeholder Email'
      - 'SPOC Name'
    Each row MUST have all three fields. If any row fails,
    we'll return a 400 error with information about the bad rows.
    """

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        csv_file_serializer = StakeHolderCSVSerializer(data=request.data)
        if not csv_file_serializer.is_valid():
            return Response(
                csv_file_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        csv_file = csv_file_serializer.validated_data["csv_file"]
        check_stakeholder_group_serializer = CheckStakeHolderGroupSerializer(
            data=request.data, context={"request": request}
        )
        if check_stakeholder_group_serializer.is_valid():
            group = check_stakeholder_group_serializer.validated_data["group"]
        else:
            return Response(
                check_stakeholder_group_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Parse the CSV
        try:
            decoded_file = csv_file.read().decode("utf-8").splitlines()
        except Exception as e:
            return Response(
                {"detail": f"Error decoding CSV file: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reader = csv.DictReader(decoded_file)
        required_columns = {"Stakeholder Name", "Stakeholder Email", "SPOC Name"}

        # Check that the CSV headers actually contain the required columns
        if not required_columns.issubset(reader.fieldnames):
            return Response(
                {
                    "detail": f"CSV must contain the columns {required_columns}. Make sure there's no extra spaces between the Rows and Columns."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        rows_to_create = []
        row_number = 2  # to track line number (row 1 is the header)
        errors = []

        for row in reader:
            # Quick presence check
            stakeholder_name = row.get("Stakeholder Name", "").strip()
            stakeholder_email = row.get("Stakeholder Email", "").strip()
            spoc_name = row.get("SPOC Name", "").strip()

            if not (stakeholder_name and stakeholder_email and spoc_name):
                errors.append(
                    f"Row {row_number}: Missing a required field. "
                    f"Values were: "
                    f"Stakeholder Name='{stakeholder_name}', "
                    f"Stakeholder Email='{stakeholder_email}', "
                    f"SPOC Name='{spoc_name}'"
                )
            else:
                # If all three fields are present, we can store them
                rows_to_create.append(
                    {
                        "name": stakeholder_name,
                        "email": stakeholder_email,
                        "poc": spoc_name,
                        "group": group.id,  # Assuming group_id is always 1 for now
                    }
                )
            row_number += 1

        # If we encountered any errors, we fail the entire request
        if errors:
            return Response(
                {"detail": "Some rows had missing fields.", "errors": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Otherwise, attempt to create the rows in the DB
        created = []
        for data in rows_to_create:
            serializer = StakeHolderSerializer(data=data)
            if serializer.is_valid():
                obj = serializer.save()
                created.append(obj.id)
            else:
                # If the serializer fails for any row, rollback
                transaction.set_rollback(True)
                return Response(
                    {
                        "detail": "Validation error while creating stakeholders",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {"detail": "All rows processed successfully!", "created_ids": created},
            status=status.HTTP_201_CREATED,
        )


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
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="stakeholders.csv"'

        writer = csv.writer(response)
        # Write the CSV header in the same format as your template
        writer.writerow(["Stakeholder Name", "Stakeholder Email", "SPOC Name"])

        # Write each stakeholder row
        for stakeholder in stakeholders_qs:
            writer.writerow([stakeholder.name, stakeholder.email, stakeholder.poc])

        return response
