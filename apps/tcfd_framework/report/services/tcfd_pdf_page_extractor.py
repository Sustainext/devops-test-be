import io
from django.template.loader import get_template
from weasyprint import HTML
from PyPDF2 import PdfReader
from apps.tcfd_framework.report.models import TCFDReport
from apps.tcfd_framework.report.serializers import TCFDReportSerializer
from apps.tcfd_framework.report.services.GetTCFDReportData import GetTCFDReportData
from rest_framework.exceptions import ValidationError


class PDFSectionPageMapper:
    """
    Service for rendering a Django template to PDF in-memory and mapping custom section markers to page (ranges).
    Usage:
        mapper = PDFSectionPageMapper("TCFD.html", context, screen_names)
        pdf_bytes = mapper.render_pdf()
        section_ranges = mapper.extract_section_page_ranges()
        # or: pdf_bytes, section_ranges = mapper.render_and_extract_ranges()
    """

    def __init__(self, marker_prefix="SCREEN_ANCHOR:"):
        self.template_name = "TCFD.html"
        self.context = None
        self.screen_names = [
            "GOV-A",
            "GOV-B",
            "STG-A",
            "STG-B",
            "STG-C",
            "RM-A",
            "RM-B",
            "RM-A",
            "M&T-A",
            "M&T-B",
            "M&T-C",
        ]
        self.marker_prefix = marker_prefix
        self.pdf_bytes = None

    def get_report_data(self, screen_name, report_id):
        try:
            tcfd_report = TCFDReport.objects.get(
                report_id=report_id, screen_name=screen_name
            )
        except TCFDReport.DoesNotExist:
            return []

        serializer = TCFDReportSerializer(tcfd_report)
        report_data = serializer.data["data"]
        return report_data

    def get_context_data(self, report):
        try:
            collect_data_object = GetTCFDReportData(report=report)
        except ValidationError:
            return ({"message": "Invalid report id"},)
        screen_name_list = [
            "message_ceo",
            "about_report",
            "about_company",
            "governance",
            "strategy",
            "risk_management",
            "metrics_targets",
            "tcfd_content_index",
            "annexure",
        ]
        all_screen_data = {}
        for screen_name in screen_name_list:
            data = collect_data_object.get_data_as_per_screen(screen_name)
            if not isinstance(data, dict):
                data = {"records": data}
            if screen_name != "tcfd_content_index":
                data["report_data"] = self.get_report_data(screen_name, report.id)
            all_screen_data[screen_name] = data

        self.context = {
            "report": report,
            **{
                f"screen_{number}": all_screen_data[screen_name]
                for number, screen_name in enumerate(screen_name_list, start=1)
            },
        }

        return self.context

    def render_pdf(self):
        html_string = get_template(self.template_name).render(self.context)
        self.pdf_bytes = HTML(string=html_string).write_pdf(target=None)
        return self.pdf_bytes

    def extract_section_page_ranges(self):
        """
        Returns: [{"screen_name": ..., "page_numbers": [start, ...end]}, ...]
        For each section, finds all pages containing its marker.
        If two or more pages are found, returns the full range from first to last.
        If only one, returns that single page.
        You can place the marker at the start and end of each section (same tag).
        """
        if self.pdf_bytes is None:
            raise RuntimeError(
                "render_pdf() must be called before extract_section_page_ranges()"
            )

        reader = PdfReader(io.BytesIO(self.pdf_bytes))
        tag_pages = {name: [] for name in self.screen_names}
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            for name in self.screen_names:
                needle = f"{self.marker_prefix}{name}"
                if needle in text:
                    tag_pages[name].append(i + 1)  # 1-based page numbers

        results = []
        for name in self.screen_names:
            pages = tag_pages[name]
            if not pages:
                page_numbers = []
            elif len(pages) == 1:
                page_numbers = [pages[0]]
            else:
                # Range from first to last including all in between
                page_numbers = list(range(pages[0], pages[-1] + 1))
            results.append({"screen_name": name, "page_numbers": page_numbers})
        return results

    def render_and_extract_ranges(self, report):
        """
        Renders PDF and extracts section page ranges in one go.
        Returns: (pdf_bytes, section_page_ranges)
        """
        self.get_context_data(report)
        self.render_pdf()
        section_page_ranges = self.extract_section_page_ranges()
        return section_page_ranges
