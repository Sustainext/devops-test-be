from weasyprint import HTML
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from sustainapp.models import Report
from apps.canada_bill_s211.v2.services.bill_s211_data import BillS211ScreenDataService
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError


class GetCanadaReportPdf(View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs.get("report_id")
        report = get_object_or_404(Report, id=report_id)

        # Step 1: Load screen data
        screen_list = list(range(1, 13))
        all_screen_data = {}
        for screen_number in screen_list:
            try:
                service = BillS211ScreenDataService(report, screen=screen_number)
                screen_data = service.get_screen_wise_data()
                all_screen_data[f"screen_{screen_number}"] = screen_data
            except ValidationError as e:
                all_screen_data[f"screen_{screen_number}"] = {"error": str(e)}

        # Step 2: Create base context with dummy TOC (for anchor detection)
        toc_items = [
            ("About the Report", "about"),
            ("1. Organization Structure", "org-structure"),
            ("2. Business Activities", "business"),
            ("3. Supply Chains", "supply"),
            ("4. Policies and Due Diligence Processes", "policies"),
            ("5. Risks of Forced Labour and Child Labour", "risks"),
            (
                "6. Steps taken to prevent and reduce risks of forced labour and child labour",
                "steps",
            ),
            ("7. Remediation Measures", "remediation"),
            ("8. Remediation of Loss of Income", "income"),
            ("9. Training on Forced Labour and Child Labour", "training"),
            ("10. Assessing Effectiveness", "effectiveness"),
            ("Approval and Attestation", "approval"),
        ]
        dummy_toc_rows = [
            {"title": title, "anchor": anchor, "page": ""}
            for title, anchor in toc_items
        ]

        context = {
            "report": report,
            "toc_rows": dummy_toc_rows,
            **{
                f"screen_{i}": all_screen_data.get(f"screen_{i}", {})
                for i in screen_list
            },
        }

        # Step 3: First render with dummy TOC to collect anchor positions
        template = get_template("canada_bills211.html")
        html_content = template.render(context, request)
        doc = HTML(string=html_content).render()

        # Step 4: Collect anchor pages
        anchor_pages = {}
        for page_num, page in enumerate(doc.pages, start=1):
            for link in page.links:
                if isinstance(link, tuple) and len(link) > 1:
                    target = link[1]
                    if target:
                        anchor_pages[target] = page_num

        # Step 5: Create final TOC rows with real page numbers
        toc_rows = [
            {"title": title, "anchor": anchor, "page": anchor_pages.get(anchor, "")}
            for title, anchor in toc_items
        ]

        # Step 6: Inject final TOC into context and render final PDF
        context["toc_rows"] = toc_rows
        final_html_content = template.render(context, request)

        response = HttpResponse(content_type="application/pdf")
        disposition = "attachment" if "download" in request.GET else "inline"
        response["Content-Disposition"] = f'{disposition}; filename="canada-report.pdf"'
        HTML(string=final_html_content).write_pdf(response)

        return response
