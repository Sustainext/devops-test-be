from rest_framework.views import APIView
import pandas as pd
from django.http import HttpResponse
import io
from django.core.files.storage import default_storage
from rest_framework.permissions import IsAuthenticated
from sustainapp.models import Report
from esg_report.utils import generate_disclosure_status


class ContentIndexExcelAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id):
        df = pd.read_excel(
            io.BytesIO(
                initial_bytes=default_storage.open(
                    "/esg_report/ContentIndex.xlsx"
                ).read()
            )
        )
        try:
            report = Report.objects.get(id=report_id, user=self.request.user)
        except Report.DoesNotExist:
            return HttpResponse("Report not found", status=404)

        statement_of_user_data = f"{report.organization.name} has reported in accordance with the GRI Standards for the period {report.start_date.strftime('%Y-%m-%d')} to {report.end_date.strftime('%Y-%m-%d')}"

        df.iloc[0, 2] = statement_of_user_data
        df.iloc[2, 2] = "Not Applicable"
        disclosure_data = generate_disclosure_status(
            report=Report.objects.get(id=report_id)
        )
        disclosure_column_index = 1
        location_column_index = 2
        omission_requirement_index = 3
        omission_reason_index = 4
        omission_explanation_index = 5
        last_row_value = df.iloc[-1, 0]

        # * Delete the last row
        df = df.drop(df.index[-1])
        for data_entry_index in range(len(disclosure_data)):
            # Prepare row data
            new_row = {
                df.columns[disclosure_column_index]: disclosure_data[data_entry_index][
                    "title"
                ],
                df.columns[location_column_index]: disclosure_data[data_entry_index][
                    "page_number"
                ],
                df.columns[omission_requirement_index]: disclosure_data[
                    data_entry_index
                ]["omission"][0]["req_omitted"],
                df.columns[omission_reason_index]: disclosure_data[data_entry_index][
                    "omission"
                ][0]["reason"],
                df.columns[omission_explanation_index]: disclosure_data[
                    data_entry_index
                ]["omission"][0]["explanation"],
            }

            # Append the new row
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.iloc[7, 0] = last_row_value
        df.columns = [
            "" if "Unnamed" in str(column) else column for column in df.columns
        ]

        # * Adding data to the dataframe
        response = HttpResponse(content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = (
            f'attachment; filename="{report.name}-Content Index.xlsx"'
        )
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Sheet1")

        response.write(buffer.getvalue())
        return response
