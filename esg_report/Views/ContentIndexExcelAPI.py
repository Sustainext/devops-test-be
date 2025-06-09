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
        try:
            report = Report.objects.get(id=report_id, user=self.request.user)
        except Report.DoesNotExist:
            return HttpResponse("Report not found", status=404)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet("GRI content index")
            writer.sheets["GRI content index"] = worksheet

            # === Styles ===
            title_fmt = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center'})
            blue_bold_white = workbook.add_format({'bold': True, 'bg_color': '#4472C4', 'color': 'white'})
            cell_fmt = workbook.add_format({'border': 1})
            header_fmt = workbook.add_format({'bold': True, 'bg_color': '#4472C4', 'color': 'white', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
            section_fmt = workbook.add_format({'bold': True, 'bg_color': '#D9D9D9', 'border': 1})
            group_fmt = workbook.add_format({'bold': True, 'bg_color': '#BDD7EE', 'border': 1, 'valign': 'vcenter'})
            omit_fmt = workbook.add_format({'border': 1, 'bg_color': '#FFD966'})
            gray_info_fmt = workbook.add_format({'italic': True, 'font_color': '#7F7F7F', 'border': 1})
            text_fmt = workbook.add_format({'border': 1})

            # === Column Widths ===
            worksheet.set_column("A:A", 28)
            worksheet.set_column("B:B", 45)
            worksheet.set_column("C:C", 20)
            worksheet.set_column("D:D", 20)
            worksheet.set_column("E:E", 20)
            worksheet.set_column("F:F", 35)
            worksheet.set_column("G:G", 25)

            # === Top Title ===
            worksheet.merge_range('A1:G1', "GRI content index", title_fmt)

            # === Top Info ===
            top_info = [
                ("Statement of use", f"{report.organization.name} has reported in accordance with the GRI Standards for the period {report.start_date} to {report.end_date}"),
                ("GRI 1 used", "GRI 1: Foundation 2021"),
                ("Applicable GRI Sector Standard(s)", "Titles of the applicable GRI Sector Standards"),
            ]
            for i, (label, value) in enumerate(top_info, start=2):
                worksheet.write(f"A{i}", label, blue_bold_white)
                worksheet.write(f"B{i}", value, cell_fmt)

            # === Table Headers with multi-row layout ===
            worksheet.merge_range("A6:A7", "GRI STANDARD/\nOTHER SOURCE", header_fmt)
            worksheet.merge_range("B6:B7", "DISCLOSURE", header_fmt)
            worksheet.merge_range("C6:C7", "LOCATION", header_fmt)
            worksheet.merge_range("D6:F6", "OMISSION", header_fmt)
            worksheet.write("D7", "REQUIREMENT(S)\nOMITTED", header_fmt)
            worksheet.write("E7", "REASON", header_fmt)
            worksheet.write("F7", "EXPLANATION", header_fmt)
            worksheet.merge_range("G6:G7", "GRI SECTOR\nSTANDARD REF. NO.", header_fmt)

            row = 7

            # === Get Disclosure Data ===
            disclosure_blocks = [
                generate_disclosure_status(report, GENERAL_DISCLOSURES_AND_PATHS, "General disclosures", is_material=False),
                generate_disclosure_status(report, MATERIAL_TOPICS_AND_PATHS, "Material topics", is_material=True),
            ]

            for block in disclosure_blocks:
                worksheet.merge_range(row, 0, row, 6, block["heading1"], section_fmt)
                row += 1

                if "items" in block:
                    items = block["items"]
                    if items:
                        worksheet.merge_range(row, 0, row + len(items) - 1, 0, "GRI 2: General Disclosures 2021", group_fmt)
                    for item in items:
                        row = self._write_disclosure_row(worksheet, row, item, "", text_fmt, omit_fmt)

                elif "sections" in block:
                    for heading2 in block["sections"]:
                        if heading2["heading2"] != block["heading1"]:
                            worksheet.merge_range(row, 0, row, 6, heading2["heading2"], section_fmt)
                            row += 1

                        for heading3 in heading2["sections"]:
                            items = heading3["items"]
                            if not items:
                                continue

                            if len(items) == 1:
                                worksheet.write(row, 0, heading3["heading3"], group_fmt)
                                row = self._write_disclosure_row(worksheet, row, items[0], "", text_fmt, omit_fmt)
                            else:
                                start_row = row
                                for item in items:
                                    row = self._write_disclosure_row(worksheet, row, item, "", text_fmt, omit_fmt)
                                worksheet.merge_range(start_row, 0, row - 1, 0, heading3["heading3"], group_fmt)

                       
            worksheet.merge_range(row, 1, row, 6, "End of Content Index", gray_info_fmt)

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = f'attachment; filename=\"{report.name}-Content Index.xlsx\"'
        response.write(buffer.getvalue())
        return response

    def _write_disclosure_row(self, sheet, row, item, group_title, text_fmt, omit_fmt):
        omission = (item.get("omission") or [{}])[0]

        if group_title:
            sheet.write(row, 0, group_title, text_fmt)
        sheet.write(row, 1, item.get("title", ""), text_fmt)
        sheet.write(row, 2, item.get("page_number", ""), text_fmt)

        for idx, key in enumerate(["req_omitted", "reason", "explanation"]):
            val = omission.get(key)
            fmt = omit_fmt if val else text_fmt
            sheet.write(row, 3 + idx, val or "", fmt)

        sheet.write(row, 6, item.get("gri_sector_no", ""), text_fmt)
        return row + 1


class ContentIndexReferenceExcelAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id):
        try:
            report = Report.objects.get(id=report_id, user=self.request.user)
        except Report.DoesNotExist:
            return HttpResponse("Report not found", status=404)

        # Define column headers
        headers = ["GRI STANDARD", "DISCLOSURE", "LOCATION"]
        df = pd.DataFrame(columns=headers)

        # Generate filled disclosure sections
        disclosure_sections = [
            *generate_disclosure_status_reference(
                report, GENERAL_DISCLOSURES_AND_PATHS, "General Disclosures", is_material=False, filter_filled=True
            ),
            *generate_disclosure_status_reference(
                report, MATERIAL_TOPICS_AND_PATHS, "Material Topics", is_material=True, filter_filled=True
            ),
        ]

        # Append disclosure rows
        for section in disclosure_sections:
            heading_display = section.get("heading1", "")  # General Disclosures, Material Topics, etc.
            first = True
            for item in section.get("items", []):
                disclosure_title = item.get("title")
                location_value = item.get("page_number") or ""
                row = {
                    "GRI STANDARD": heading_display if first else "",
                    "DISCLOSURE": disclosure_title,
                    "LOCATION": location_value
                }
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                first = False

        # Prepare Excel writer
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            workbook = writer.book
            worksheet_name = "Sheet1"
            df.to_excel(writer, index=False, sheet_name=worksheet_name, startrow=5)

            worksheet = writer.sheets[worksheet_name]

            # Formats
            bold_format = workbook.add_format({'bold': True})
            title_format = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center'})
            merge_format = workbook.add_format({'align': 'left', 'valign': 'vcenter'})
            end_format = workbook.add_format({'bold': True, 'align': 'left'})
            label_format = workbook.add_format({
                'bold': True,
                'bg_color': "#7FABC6",  # light grey background
                'valign': 'vcenter'
            })
            # Write top rows with formatting
            worksheet.merge_range("A1:C1", "GRI content index", title_format)
            worksheet.write("A2", "Statement of use", label_format)
            worksheet.merge_range("B2:C2", f"{report.organization.name} has reported the information cited in this GRI content index "
                                           f"for the period {report.start_date.strftime('%Y-%m-%d')} to {report.end_date.strftime('%Y-%m-%d')} "
                                           f"with reference to the GRI Standards.", merge_format)
            worksheet.write("A3", "GRI 1 used", label_format)
            worksheet.write("B3", "GRI 1: Foundation 2021")

           
            # Bold column headers manually
            # Create header style with background color
            header_format = workbook.add_format({
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': "#9AC8ED",  # Light blue
                'border': 1
            })

            # Apply to column headers (Row 6, index=5)
            for col_num, value in enumerate(headers):
                worksheet.write(5, col_num, value, header_format)


            # Autofit columns
            worksheet.set_column("A:A", 40)
            worksheet.set_column("B:B", 65)
            worksheet.set_column("C:C", 30)

            # Write "End of Content Index" at the end in DISCLOSURE column
            end_row = df.shape[0] + 6  # since we start at row=5
            worksheet.write(f'B{end_row + 1}', "End of Content Index", end_format)

        buffer.seek(0)

        disposition = "attachment" if "download" in request.GET else "inline"
        response = HttpResponse(
            buffer.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'{disposition}; filename="{report.name}-ContentIndex-Reference.xlsx"'
        return response


