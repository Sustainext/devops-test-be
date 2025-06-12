import json
from esg_report.models.ESGCustomReport import EsgCustomReport


class CustomEsgReportValidator:
    def section_data(self):
        section = {}
        with open("esg_report/Utils/section.json", "r") as f:
            section = json.load(f)
        return section

    def sub_section_data(self):
        sub_section = {}
        with open("esg_report/Utils/sub_section.json", "r") as f:
            sub_section = json.load(f)
        return sub_section

    def filter_sub_section(self, sub_section, include_management_material_topics):
        if include_management_material_topics:
            return sub_section  # No filtering needed

        for section_items in sub_section.values():
            if not isinstance(section_items, list):
                continue

            for item in section_items:
                children = item.get("children")
                if isinstance(children, list):
                    # Filter only if 'children' list is not empty
                    item["children"] = [
                        child
                        for child in children
                        if child.get("label", "").strip().lower()
                        not in [
                            "management of material topic",
                            "management of material topics",
                        ]
                    ]

        return sub_section

    def create_custom_report(
        self, report_id, include_management_material_topics, include_content_index
    ):
        EsgCustomReport.objects.create(
            report_id=report_id,
            section=self.section_data(),
            sub_section=self.filter_sub_section(
                self.sub_section_data(), include_management_material_topics
            ),
            include_management_material_topics=include_management_material_topics,
            include_content_index=include_content_index,
        )
