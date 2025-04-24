import os
import json
from django.core.management.base import BaseCommand
from geo_data.models import Country, State

class Command(BaseCommand):
    help = 'Load state data from JSON file into the database'

    def handle(self, *args, **options):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'state.json')

        with open(file_path, 'r') as file:
            data = json.load(file)
            states_data = data[2]['data']

            for state in states_data:
                try:
                    country = Country.objects.get(id=state['country_id'])
                    State.objects.create(
                        country=country,
                        state_name=state['state_name']
                    )
                except Country.DoesNotExist:
                    self.stderr.write(f"Country ID {state['country_id']} not found.")

        self.stdout.write(self.style.SUCCESS('Successfully loaded state data'))
