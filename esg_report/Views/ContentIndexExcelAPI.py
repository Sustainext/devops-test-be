from rest_framework.views import APIView
import pandas as pd
from django.http import HttpResponse
import io
from django.core.files.storage import default_storage
from rest_framework.permissions import IsAuthenticated
from sustainapp.models import Report
from esg_report.utils import generate_disclosure_status,generate_disclosure_status_reference
from common.enums.GeneralTopicDisclosuresAndPaths import GENERAL_DISCLOSURES_AND_PATHS
from common.enums.ManagementMatearilTopicsAndPaths import MATERIAL_TOPICS_AND_PATHS


class ContentIndexExcelAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id):
        df = pd.read_excel(
            io.BytesIO(
                initial_bytes=default_storage.open(
                    "esg_report/ContentIndex.xlsx"
                ).read()
            )
        )

        try:
            report = Report.objects.get(id=report_id, user=self.request.user)
        except Report.DoesNotExist:
            return HttpResponse("Report not found", status=404)

        # Statement in cell (0,2)
        statement_of_user_data = (
            f"{report.organization.name} has reported in accordance with the GRI Standards "
            f"for the period {report.start_date.strftime('%Y-%m-%d')} to {report.end_date.strftime('%Y-%m-%d')}"
        )
        df.iloc[0, 2] = statement_of_user_data
        df.iloc[2, 2] = "Not Applicable"

        # Get full disclosure data
        disclosure_blocks = [
            generate_disclosure_status(report, GENERAL_DISCLOSURES_AND_PATHS, "General Disclosures", is_material=False),
            generate_disclosure_status(report, MATERIAL_TOPICS_AND_PATHS, "Material Topics", is_material=True),
        ]

        disclosure_column_index = 1
        location_column_index = 2
        omission_requirement_index = 3
        omission_reason_index = 4
        omission_explanation_index = 5
        last_row_value = df.iloc[-1, 0]

        # Remove the last row to append cleanly
        df = df.drop(df.index[-1])

        # Flatten disclosure sections
        flattened_disclosures = []
        for block in disclosure_blocks:
            if "items" in block:
                flattened_disclosures.extend(block["items"])
            elif "sections" in block:
                for section in block["sections"]:
                    for sub_section in section["sections"]:
                        flattened_disclosures.extend(sub_section["items"])

        # Append each disclosure as a new row in the DataFrame
        for data in flattened_disclosures:
            new_row = {
                df.columns[disclosure_column_index]: data["title"],
                df.columns[location_column_index]: data.get("page_number"),
                df.columns[omission_requirement_index]: data["omission"][0].get("req_omitted"),
                df.columns[omission_reason_index]: data["omission"][0].get("reason"),
                df.columns[omission_explanation_index]: data["omission"][0].get("explanation"),
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        # Restore last row if needed
        df.iloc[7, 0] = last_row_value

        # Clean unnamed column headers
        df.columns = ["" if "Unnamed" in str(col) else col for col in df.columns]

        # Export Excel
        disposition = "attachment" if "download" in request.GET else "inline"
        response = HttpResponse(content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = (
            f'{disposition}; filename="{report.name}-Content Index.xlsx"'
        )
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Sheet1")

        response.write(buffer.getvalue())
        return response
  

class ContentIndexReferenceExcelAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id):
        try:
            report = Report.objects.get(id=report_id,  user=self.request.user)
        except Report.DoesNotExist:
            return HttpResponse("Report not found", status=404)

        # Load Excel template
        try:
            df = pd.read_excel(
                io.BytesIO(
                    default_storage.open("esg_report/ContentIndex.xlsx").read()
                )
            )
        except Exception as e:
            return HttpResponse(f"Template error: {str(e)}", status=500)

        # Safe header write
        statement = (
            f"{report.organization.name} has reported in reference to the GRI Standards "
            f"for the period {report.start_date.strftime('%Y-%m-%d')} to {report.end_date.strftime('%Y-%m-%d')}"
        )
        if df.shape[0] > 0 and df.shape[1] > 2:
            df.iloc[0, 2] = statement
        if df.shape[0] > 2 and df.shape[1] > 2:
            df.iloc[2, 2] = "Reference Only"

        # Fetch only filled disclosures using same logic as API
        disclosure_sections = [
            *generate_disclosure_status_reference(
                report, GENERAL_DISCLOSURES_AND_PATHS, "General Disclosures", is_material=False, filter_filled=True
            ),
            *generate_disclosure_status_reference(
                report, MATERIAL_TOPICS_AND_PATHS, "Material Topics", is_material=True, filter_filled=True
            ),
        ]

        # Drop last row before appending to prevent template footer issues
        df = df.drop(df.index[-1]) if df.shape[0] > 0 else df

        # Column mapping
        disclosure_col = 1
        location_col = 2
        omission_req_col = 3
        omission_reason_col = 4
        omission_explanation_col = 5

        for section in disclosure_sections:
            heading = section.get("heading1")
            for item in section.get("items", []):
                title = item["title"]
                location = item.get("page_number")
                omission = item.get("omission", [{}])[0]  # Get omission details

                new_row = {
                    df.columns[disclosure_col]: f"{title}",
                    df.columns[location_col]: location,
                    df.columns[omission_req_col]: omission.get("req_omitted"),
                    df.columns[omission_reason_col]: omission.get("reason"),
                    df.columns[omission_explanation_col]: omission.get("explanation"),
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        # Reapply footer
        footer = ["End of Content Index"]
        df = pd.concat([df, pd.DataFrame([[*footer]])], ignore_index=True)

        # Clean column headers
        df.columns = ["" if "Unnamed" in str(col) else col for col in df.columns]

        # Generate Excel response
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Sheet1")

        disposition = "attachment" if "download" in request.GET else "inline"
        response = HttpResponse(buffer.getvalue(), content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = f'{disposition}; filename="{report.name}-Content Index Reference.xlsx"'

        return response
