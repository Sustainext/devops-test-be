import requests
from django.core.management.base import BaseCommand
from datametric.models import EmissionFactor
import os


class Command(BaseCommand):
    help = "Efficiently imports emission factors from Climatiq API using bulk insert"

    def handle(self, *args, **options):
        api_key = os.getenv("CLIMATIQ_AUTH_TOKEN")
        if not api_key:
            self.stderr.write(
                self.style.ERROR("CLIMATIQ_AUTH_TOKEN not found in environment.")
            )
            return

        headers = {"Authorization": f"Bearer {api_key}"}
        base_url = "https://api.climatiq.io/data/v1/search"
        params = {"data_version": 20, "results_per_page": 400}

        page = 1
        total_created = 0

        self.stdout.write("Starting fast bulk import from Climatiq...")

        while True:
            params["page"] = page
            response = requests.get(base_url, headers=headers, params=params)
            data = response.json()

            results = data.get("results", [])
            if not results:
                break

            to_create = []

            for item in results:
                ef = EmissionFactor(
                    factor_id=item["id"],
                    activity_id=item["activity_id"],
                    name=item["name"],
                    category=item["category"],
                    sector=item["sector"],
                    source=item["source"],
                    source_link=item.get("source_link"),
                    source_dataset=item["source_dataset"],
                    uncertainty=item.get("uncertainty"),
                    year=item["year"],
                    year_released=item["year_released"],
                    region=item["region"],
                    region_name=item["region_name"],
                    description=item["description"],
                    unit_type=item["unit_type"],
                    unit=item["unit"],
                    source_lca_activity=item.get("source_lca_activity"),
                    data_quality_flags=item.get("data_quality_flags", []),
                    access_type=item["access_type"],
                    supported_calculation_methods=item.get(
                        "supported_calculation_methods", []
                    ),
                    factor=item["factor"],
                    factor_calculation_method=item["factor_calculation_method"],
                    factor_calculation_origin=item["factor_calculation_origin"],
                    constituent_gases=item.get("constituent_gases", {}),
                    data_version=item.get("data_version", {}),
                    data_version_information=item.get("data_version_information", {}),
                    possible_filters=item.get("possible_filters"),
                )
                to_create.append(ef)

            # Bulk insert, skip duplicates (based on factor_id being unique)
            EmissionFactor.objects.bulk_create(to_create, ignore_conflicts=True)
            total_created += len(to_create)

            self.stdout.write(
                f"Page {page} done. Total imported so far: {total_created}"
            )

            if page >= data.get("last_page", page):
                break
            page += 1

        self.stdout.write(
            self.style.SUCCESS(f"Finished. Total factors imported: {total_created}")
        )
