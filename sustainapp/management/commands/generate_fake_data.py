import os
import django
from django.core.management.base import BaseCommand
from faker import Faker
from sustainapp.models import Client, Organization, Corporateentity, Location
import uuid
import multiprocessing
from django.db import transaction
import time
import asyncio
from asgiref.sync import sync_to_async, async_to_sync
from datametric.models import DataPoint, Path, DataMetric, RawResponse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "azureproject.settings")
django.setup()


def generate_clients(num_records):
    fake = Faker()
    return [
        Client(
            name=f"{fake.name()}_{uuid.uuid4().hex[:8]}",
            customer=fake.boolean(),
        )
        for _ in range(num_records)
    ]


def generate_organizations(args):
    num_records, client_ids = args
    fake = Faker()
    return [
        Organization(
            name=f"{fake.company()}_{uuid.uuid4().hex[:8]}",
            client_id=fake.random_element(client_ids),
        )
        for _ in range(num_records)
    ]


def generate_corporate_entities(args):
    num_records, client_ids = args
    fake = Faker()
    return [
        Corporateentity(
            name=f"{fake.company()}_{uuid.uuid4().hex[:8]}",
            client_id=fake.random_element(client_ids),
        )
        for _ in range(num_records)
    ]


async def bulk_insert_clients(clients):
    await sync_to_async(Client.objects.bulk_create)(clients, batch_size=len(clients))


async def bulk_insert_organizations(organizations):
    await sync_to_async(Organization.objects.bulk_create)(
        organizations, batch_size=len(organizations)
    )


class Command(BaseCommand):
    help = "Generate a large amount of fake data for Client and Organization, Corporate, Location models"

    def handle(self, *args, **kwargs):
        async_to_sync(self.generate_data)()

    async def generate_data(self):
        batch_size = 10000
        total_records = 500_000  # Reduced for testing
        max_workers = multiprocessing.cpu_count()

        start_time = time.time()

        self.stdout.write("Starting client generation")

        # Generate Clients
        with multiprocessing.Pool(processes=max_workers) as pool:
            clients_batches = pool.map(
                generate_clients, [batch_size] * (total_records // batch_size)
            )

        self.stdout.write("Inserting generated clients into database")
        await asyncio.gather(
            *[bulk_insert_clients(clients) for clients in clients_batches]
        )
        self.stdout.write("Finished client generation")

        # Fetch client IDs
        self.stdout.write("Fetching client IDs")
        client_ids = await sync_to_async(list)(
            Client.objects.values_list("id", flat=True)
        )
        self.stdout.write(f"Fetched {len(client_ids)} client IDs")

        self.stdout.write("Starting organization generation")

        # Generate Organizations
        with multiprocessing.Pool(processes=max_workers) as pool:
            organizations_batches = pool.map(
                generate_organizations,
                [(batch_size, client_ids)] * (total_records // batch_size),
            )

        self.stdout.write("Inserting generated organizations into database")
        await asyncio.gather(
            *[
                bulk_insert_organizations(organizations)
                for organizations in organizations_batches
            ]
        )

        end_time = time.time()
        total_time = end_time - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully generated fake data in {total_time:.2f} seconds"
            )
        )
