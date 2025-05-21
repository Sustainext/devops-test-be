import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connections
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
import logging

from sustainapp.models import Client, Organization, Corporateentity as Corporate, Location, Framework as SustainAppFramework
from datametric.models import RawResponse, Path

logger = logging.getLogger("django") # Use this for detailed logging
# For less verbose console output, we can use self.stdout.write

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates a new client and copies RawResponse data from another client. Signals for RawResponse will be triggered.'

    def add_arguments(self, parser):
        parser.add_argument('--DBHOST', type=str, required=True, help='Source database host')
        parser.add_argument('--DBNAME', type=str, required=True, help='Source database name')
        parser.add_argument('--DBUSER', type=str, required=True, help='Source database user')
        parser.add_argument('--DBPASS', type=str, required=True, help='Source database password')
        parser.add_argument('--DBPORT', type=str, required=True, help='Source database port')
        parser.add_argument('--admin-username', type=str, required=True,
                          help='Admin user username to associate with the new client and data')
        parser.add_argument('--client-name', type=str, required=True,
                          help='Source client name to copy data from')

    def handle(self, *args, **options):
        # Connect to source database using Django ORM
        try:
            connections.databases['source'] = {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': options['DBNAME'],
                'USER': options['DBUSER'],
                'PASSWORD': options['DBPASS'],
                'HOST': options['DBHOST'],
                'PORT': options['DBPORT'],
                'OPTIONS': {},
                'TIME_ZONE': None,
                'CONN_MAX_AGE': 0,
                'CONN_HEALTH_CHECKS': False,
                'AUTOCOMMIT': True,
                'ATOMIC_REQUESTS': False,
                'TEST': {'CHARSET': None, 'COLLATION': None, 'MIGRATE': True, 'MIRROR': None, 'NAME': None}
            }
            self.stdout.write(self.style.SUCCESS(f"Configured connection to source database: {options['DBNAME']}"))

            try:
                connections['source'].ensure_connection()
                self.stdout.write(self.style.SUCCESS("Connection to source database successful!"))
            except Exception as e:
                logger.error(f"Error connecting to source DB: {e}", exc_info=True)
                raise CommandError(f"Failed to connect to source database: {e}")

        except Exception as e:
            logger.error(f"Error configuring source DB: {e}", exc_info=True)
            raise CommandError(f"Failed to configure source database connection: {e}")

        now = timezone.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        new_client_name = f"{options['client_name']} Copy {date_str} {time_str}"

        with transaction.atomic(): # All operations within this block are atomic for the default DB
            try:
                try:
                    admin_user = User.objects.get(username=options['admin_username'])
                except User.DoesNotExist:
                    raise CommandError(f"Admin user with username '{options['admin_username']}' not found in target database. Command aborted.")

                new_client = Client.objects.create(name=new_client_name)
                self.stdout.write(self.style.SUCCESS(f"Created new client: {new_client.name} (ID: {new_client.id})"))

                try:
                    source_client = Client.objects.using('source').get(name=options['client_name'])
                    self.stdout.write(self.style.SUCCESS(f"Found source client: {source_client.name} (ID: {source_client.id}) in source DB"))
                except Client.DoesNotExist:
                    raise CommandError(f"Source client with name '{options['client_name']}' not found in source database '{options['DBNAME']}'.")

                # 1. Fetch and create Organizations
                source_orgs = Organization.objects.using('source').filter(client=source_client)
                self.stdout.write(f"Found {source_orgs.count()} organizations to copy for source client '{source_client.name}'")
                org_map = {}

                for source_org in source_orgs:
                    new_org_data = {
                        field.name: getattr(source_org, field.name)
                        for field in Organization._meta.fields
                        if field.name not in ['id', 'client']
                    }
                    new_org = Organization.objects.create(client=new_client, **new_org_data)
                    org_map[source_org.id] = new_org
                    self.stdout.write(f"  Created organization: {new_org.name} (New ID: {new_org.id}, Source ID: {source_org.id})")

                    m2m_fields_to_copy = ['framework', 'sdg', 'rating', 'certification', 'target', 'regulation']
                    for field_name in m2m_fields_to_copy:
                        if hasattr(source_org, field_name) and hasattr(new_org, field_name):
                            source_m2m_manager = getattr(source_org, field_name)
                            new_m2m_manager = getattr(new_org, field_name)
                            target_items_to_add = []
                            for item in source_m2m_manager.all():
                                try:
                                    target_item = type(item).objects.get(name=item.name) # Assumes 'name' is unique for these M2M related models
                                    target_items_to_add.append(target_item)
                                except type(item).DoesNotExist:
                                    logger.warning(f"M2M Copy for Org '{new_org.name}': Could not find matching {field_name} '{item.name}' in target DB. Skipping this item.")
                                    self.stdout.write(self.style.WARNING(f"    Could not find matching {field_name} '{item.name}' for org '{new_org.name}'. Skipping."))
                                except Exception as e_m2m:
                                    logger.error(f"M2M Copy for Org '{new_org.name}': Error finding/adding {field_name} '{item.name}': {e_m2m}", exc_info=True)
                                    self.stdout.write(self.style.WARNING(f"    Error finding/adding {field_name} '{item.name}' for org '{new_org.name}': {e_m2m}"))
                            if target_items_to_add:
                                new_m2m_manager.add(*target_items_to_add)
                                # self.stdout.write(f"    Copied {len(target_items_to_add)} {field_name}(s) to organization: {new_org.name}")


                    if hasattr(new_org, 'framework') and not new_org.framework.exists():
                        try:
                            default_framework, created = SustainAppFramework.objects.get_or_create(
                                name="GRI: With reference to",
                                defaults={"Image": "images/framework/GRI.png"}
                            )
                            new_org.framework.add(default_framework)
                            # style = self.style.SUCCESS if created else self.style.NOTICE
                            # self.stdout.write(style(f"    Added default framework '{default_framework.name}' to organization: {new_org.name}"))
                        except Exception as e_df:
                            logger.warning(f"Could not add default framework to org {new_org.name}: {e_df}", exc_info=True)
                            self.stdout.write(self.style.WARNING(f"    Could not add default framework to org {new_org.name}: {e_df}"))

                # 2. Fetch and create Corporates
                source_corporates = Corporate.objects.using('source').filter(
                    client=source_client,
                    organization_id__in=org_map.keys()
                )
                self.stdout.write(f"Found {source_corporates.count()} corporate entities to copy")
                corporate_map = {}

                for source_corp in source_corporates:
                    mapped_new_org = org_map.get(source_corp.organization_id)
                    if not mapped_new_org:
                        logger.warning(f"Skipping corporate '{source_corp.name}' (Source ID: {source_corp.id}) as its organization (Source ID: {source_corp.organization_id}) was not mapped.")
                        self.stdout.write(self.style.WARNING(f"  Skipping corporate '{source_corp.name}' as its org was not mapped."))
                        continue
                    new_corp_data = {
                        field.name: getattr(source_corp, field.name)
                        for field in Corporate._meta.fields
                        if field.name not in ['id', 'client', 'organization']
                    }
                    new_corp = Corporate.objects.create(client=new_client, organization=mapped_new_org, **new_corp_data)
                    corporate_map[source_corp.id] = new_corp
                    self.stdout.write(f"  Created corporate: {new_corp.name} (New ID: {new_corp.id}, Source ID: {source_corp.id}) for Org: {mapped_new_org.name}")

                    m2m_fields_to_copy_corp = ['framework', 'rating', 'certification', 'target', 'regulation']
                    for field_name in m2m_fields_to_copy_corp:
                        if hasattr(source_corp, field_name) and hasattr(new_corp, field_name):
                            source_m2m_manager = getattr(source_corp, field_name)
                            new_m2m_manager = getattr(new_corp, field_name)
                            target_items_to_add = []
                            for item in source_m2m_manager.all():
                                try:
                                    target_item = type(item).objects.get(name=item.name)
                                    target_items_to_add.append(target_item)
                                except type(item).DoesNotExist:
                                    logger.warning(f"M2M Copy for Corp '{new_corp.name}': Could not find matching {field_name} '{item.name}' in target DB. Skipping this item.")
                                    self.stdout.write(self.style.WARNING(f"    Could not find matching {field_name} '{item.name}' for corp '{new_corp.name}'. Skipping."))
                                except Exception as e_m2m_corp:
                                    logger.error(f"M2M Copy for Corp '{new_corp.name}': Error finding/adding {field_name} '{item.name}': {e_m2m_corp}", exc_info=True)
                                    self.stdout.write(self.style.WARNING(f"    Error finding/adding {field_name} '{item.name}' for corp '{new_corp.name}': {e_m2m_corp}"))
                            if target_items_to_add:
                                new_m2m_manager.add(*target_items_to_add)
                                # self.stdout.write(f"    Copied {len(target_items_to_add)} {field_name}(s) to corporate: {new_corp.name}")


                # 3. Fetch and create Locations
                source_locations = Location.objects.using('source').filter(
                    client=source_client,
                    corporateentity_id__in=corporate_map.keys()
                )
                self.stdout.write(f"Found {source_locations.count()} locations to copy")
                location_map = {}

                for source_loc in source_locations:
                    mapped_new_corp = corporate_map.get(source_loc.corporateentity_id)
                    if not mapped_new_corp:
                        logger.warning(f"Skipping location '{source_loc.name}' (Source ID: {source_loc.id}) as its corporate entity (Source ID: {source_loc.corporateentity_id}) was not mapped.")
                        self.stdout.write(self.style.WARNING(f"  Skipping location '{source_loc.name}' as its corporate entity was not mapped."))
                        continue
                    new_loc_data = {
                        field.name: getattr(source_loc, field.name)
                        for field in Location._meta.fields
                        if field.name not in ['id', 'client', 'corporateentity']
                    }
                    new_loc = Location.objects.create(client=new_client, corporateentity=mapped_new_corp, **new_loc_data)
                    location_map[source_loc.id] = new_loc
                    self.stdout.write(f"  Created location: {new_loc.name} (New ID: {new_loc.id}, Source ID: {source_loc.id}) for Corporate: {mapped_new_corp.name}")


                # 4. Fetch/Create Paths
                source_raw_responses_path_ids = RawResponse.objects.using('source').filter(client=source_client).values_list('path_id', flat=True).distinct()
                source_paths_qs = Path.objects.using('source').filter(id__in=source_raw_responses_path_ids)
                self.stdout.write(f"Found {source_paths_qs.count()} unique paths referenced by RawResponses to copy/map")
                path_map = {}

                for source_path in source_paths_qs:
                    try:
                        new_path, created = Path.objects.get_or_create(
                            slug=source_path.slug,
                            defaults={'name': source_path.name, 'disclosure': None}
                        )
                        path_map[source_path.id] = new_path
                        # if created:
                        #     self.stdout.write(f"  Created path: {new_path.slug} (New ID: {new_path.id})")
                        # else:
                        #     self.stdout.write(self.style.NOTICE(f"  Using existing path: {new_path.slug} (ID: {new_path.id})"))
                    except Exception as e_path:
                        logger.error(f"Could not copy/map path {source_path.slug} (Source ID: {source_path.id}): {e_path}", exc_info=True)
                        self.stdout.write(self.style.WARNING(f"  Could not copy/map path {source_path.slug} (Source ID: {source_path.id}): {e_path}"))


                # 5. Fetch and create RawResponses (individually to trigger signals)
                source_raw_responses_qs = RawResponse.objects.using('source').filter(client=source_client)
                total_source_rr_count = source_raw_responses_qs.count() # Get count beforehand for progress
                self.stdout.write(f"Found {total_source_rr_count} raw responses to copy for source client '{source_client.name}'")

                failed_raw_responses_info = []
                copied_rr_count = 0
                progress_interval = 100 # Log progress every 100 RRs or adjust as needed

                # Iterate over RawResponse queryset to avoid loading all into memory at once
                for i, source_rr in enumerate(source_raw_responses_qs.iterator()):
                    if (i + 1) % progress_interval == 0:
                        self.stdout.write(f"  Processing RawResponse {i + 1}/{total_source_rr_count}...")

                    new_path = path_map.get(source_rr.path_id)
                    if not new_path:
                        msg = f"Skipping RawResponse (Source ID: {source_rr.id}) - Mapped Path not found for source Path ID {source_rr.path_id}."
                        logger.warning(msg)
                        failed_raw_responses_info.append({'source_id': source_rr.id, 'error': msg})
                        continue

                    new_organization = org_map.get(source_rr.organization_id) if source_rr.organization_id else None
                    new_corporate = corporate_map.get(source_rr.corporate_id) if source_rr.corporate_id else None
                    new_locale = location_map.get(source_rr.locale_id) if source_rr.locale_id else None

                    if source_rr.organization_id and not new_organization:
                         logger.warning(f"RawResponse (Source ID: {source_rr.id}): Organization (Source ID: {source_rr.organization_id}) was in source but not found in map for new client. Setting to None.")
                    if source_rr.corporate_id and not new_corporate:
                         logger.warning(f"RawResponse (Source ID: {source_rr.id}): Corporate (Source ID: {source_rr.corporate_id}) was in source but not found in map for new client. Setting to None.")
                    if source_rr.locale_id and not new_locale:
                         logger.warning(f"RawResponse (Source ID: {source_rr.id}): Locale/Location (Source ID: {source_rr.locale_id}) was in source but not found in map for new client. Setting to None.")

                    try:
                        new_rr = RawResponse(
                            data=source_rr.data,
                            path=new_path,
                            user=admin_user,
                            client=new_client,
                            organization=new_organization,
                            corporate=new_corporate,
                            locale=new_locale,
                            year=source_rr.year,
                            month=source_rr.month
                            # Add any other fields that need to be copied from source_rr
                        )
                        new_rr.save() # This will trigger signals
                        copied_rr_count += 1
                    except Exception as e_rr_save:
                        error_msg = f"Failed to save RawResponse (Source ID: {source_rr.id}): {e_rr_save}"
                        logger.error(error_msg, exc_info=True)
                        failed_raw_responses_info.append({'source_id': source_rr.id, 'error': error_msg})

                self.stdout.write(f"\nProcessed {total_source_rr_count} source RawResponses.")
                self.stdout.write(self.style.SUCCESS(f"Successfully created {copied_rr_count} RawResponses (signals triggered)."))

                if failed_raw_responses_info:
                    self.stdout.write(self.style.ERROR(f"Encountered issues with {len(failed_raw_responses_info)} RawResponses:"))
                    # Log all failures to the logger
                    for failure in failed_raw_responses_info:
                        logger.error(f"Failed RawResponse Detail: Source ID: {failure['source_id']}, Error: {failure['error']}")
                    # Print a summary to stdout
                    for failure in failed_raw_responses_info[:10]: # Display first 10 failures in console
                        self.stdout.write(self.style.ERROR(f"  Source RR ID: {failure['source_id']}, Error: {failure['error']}"))
                    if len(failed_raw_responses_info) > 10:
                        self.stdout.write(self.style.ERROR(f"  ... and {len(failed_raw_responses_info) - 10} more failures (see logs for all details)."))
                elif copied_rr_count == total_source_rr_count :
                     self.stdout.write(self.style.SUCCESS("All RawResponses copied successfully!"))


            except Exception as e:
                logger.error(f"An error occurred during the atomic copying process: {e}", exc_info=True)
                raise CommandError(f"Copying process failed and was rolled back: {e}")

        self.stdout.write(self.style.SUCCESS('Data copying process complete.'))

        if 'source' in connections.databases:
            del connections.databases['source']
            if 'source' in connections:
                 del connections['source']
            self.stdout.write(self.style.SUCCESS("Source database connection configuration removed."))
