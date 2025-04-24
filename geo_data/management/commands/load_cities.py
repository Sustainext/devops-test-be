# import os
# import json
# from django.core.management.base import BaseCommand
# from geo_data.models import State, City

# class Command(BaseCommand):
#     help = 'Load city data from JSON file into the database'

#     def handle(self, *args, **options):
#         base_dir = os.path.dirname(__file__)
#         file_path = os.path.join(base_dir, 'city.json')

#         with open(file_path, 'r') as file:
#             data = json.load(file)
#             cities_data = data[2]['data']

#             for city in cities_data:
#                 try:
#                     state = State.objects.get(state_id=city['state_id'])
#                     City.objects.create(
#                         city_id=city['city_id'],
#                         state=state,
#                         city_name=city['city_name']
#                     )
#                 except State.DoesNotExist:
#                     self.stderr.write(f"State ID {city['state_id']} not found.")

#         self.stdout.write(self.style.SUCCESS('Successfully loaded city data'))

import os
import json
from django.core.management.base import BaseCommand
from geo_data.models import State, City
from django.db import transaction

class Command(BaseCommand):
    help = 'Load city data from JSON file into the database'

    def handle(self, *args, **options):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'city.json')

        with open(file_path, 'r') as file:
            data = json.load(file)
            cities_data = data[2].get('data', [])

            with transaction.atomic():
                for city in cities_data:
                    try:
                        state = State.objects.get(id=city.get('state_id'))
                        City.objects.create(
                            state=state,
                            city_name=city.get('city_name')
                        )
                    except State.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"State ID {city.get('state_id')} not found."))
                    except KeyError as e:
                        self.stdout.write(self.style.WARNING(f"Missing key: {str(e)} in city data."))

        self.stdout.write(self.style.SUCCESS('Successfully loaded city data'))
