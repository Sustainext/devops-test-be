import os
import json
from django.core.management.base import BaseCommand
from geo_data.models import Country

class Command(BaseCommand):
    help = 'Load country data from JSON file into the database'

    def handle(self, *args, **options):
        # Get the directory of the current script
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'country.json')

        with open(file_path, 'r') as file:
            data = json.load(file)
            countries_data = data[2]['data']

            for country in countries_data:
                Country.objects.create(
                    sortname=country['sortname'],
                    country_name=country['country_name'],
                    slug=country['slug'],
                    # status=country['status']
                )

        self.stdout.write(self.style.SUCCESS('Successfully loaded country data'))
