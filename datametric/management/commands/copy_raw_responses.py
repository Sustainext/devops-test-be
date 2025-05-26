import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connections
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings # Not strictly used if connections.databases is modified directly, but good practice
import logging

from sustainapp.models import Client, Organization, Corporateentity as Corporate, Location, Framework as SustainAppFramework
from datametric.models import RawResponse, Path

logger = logging.getLogger("django") # Use this for detailed logging

User = get_user_model()


class Command(BaseCommand):
    help = ('Creates a new client and copies RawResponse data from another client. '
            'Uses ONLY EXISTING Paths in the target DB; RawResponses for non-existing paths are skipped. '
            'Signals for RawResponse will be triggered during individual saves.')

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
        # 1. Connect to source database
        self.stdout.write(self.style.MIGRATE_HEADING("Step 1: Configuring and connecting to source database..."))
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
            self.stdout.write(self.style.SUCCESS(f"  Configured connection to source database: {options['DBNAME']} on {options['DBHOST']}"))

            try:
                connections['source'].ensure_connection()
                self.stdout.write(self.style.SUCCESS("  Connection to source database successful!"))
            except Exception as e:
                logger.error(f"Error connecting to source DB: {e}", exc_info=True)
                raise CommandError(f"Failed to connect to source database: {e}")

        except Exception as e:
            logger.error(f"Error configuring source DB: {e}", exc_info=True)
            raise CommandError(f"Failed to configure source database connection: {e}")

        now = timezone.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        new_client_name_generated = f"{options['client_name']} Copy {date_str} {time_str}"
        new_client_instance = None # Will hold the created Client object

        # All subsequent operations are within a transaction on the default (target) database
        with transaction.atomic():
            try:
                # 2. Create New Client and Get Admin User
                self.stdout.write(self.style.MIGRATE_HEADING(f"\nStep 2: Preparing target client '{new_client_name_generated}'..."))
                try:
                    admin_user = User.objects.get(username=options['admin_username'])
                    self.stdout.write(self.style.SUCCESS(f"  Found admin user '{admin_user.username}' in target database."))
                except User.DoesNotExist:
                    raise CommandError(f"Admin user with username '{options['admin_username']}' not found in target database. Command aborted.")

                new_client_instance = Client.objects.create(name=new_client_name_generated)
                self.stdout.write(self.style.SUCCESS(f"  Created new client: {new_client_instance.name} (ID: {new_client_instance.id}) in target database."))

                # Find source client
                try:
                    source_client = Client.objects.using('source').get(name=options['client_name'])
                    self.stdout.write(self.style.SUCCESS(f"  Found source client: {source_client.name} (ID: {source_client.id}) in source database '{options['DBNAME']}'."))
                except Client.DoesNotExist:
                    raise CommandError(f"Source client with name '{options['client_name']}' not found in source database '{options['DBNAME']}'.")


                # 3. Copy Organizations, Corporates, Locations
                self.stdout.write(self.style.MIGRATE_HEADING(f"\nStep 3: Copying hierarchy (Organizations, Corporates, Locations) for new client '{new_client_instance.name}'..."))

                # 3a. Fetch and create Organizations
                source_orgs = Organization.objects.using('source').filter(client=source_client)
                self.stdout.write(f"  Found {source_orgs.count()} organizations to copy from source client '{source_client.name}'.")
                org_map = {} # Maps source_org.id to new_org object

                for source_org in source_orgs.iterator(): # Use iterator for potentially large querysets
                    new_org_data = {
                        field.name: getattr(source_org, field.name)
                        for field in Organization._meta.fields
                        if field.name not in ['id', 'client'] # Exclude PK and FK to client
                    }
                    new_org = Organization.objects.create(client=new_client_instance, **new_org_data)
                    org_map[source_org.id] = new_org
                    # self.stdout.write(f"    Created organization: {new_org.name} (New ID: {new_org.id}, Source ID: {source_org.id})")

                    # Copy M2M fields for Organization
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
                                except Exception as e_m2m:
                                    logger.error(f"M2M Copy for Org '{new_org.name}': Error finding/adding {field_name} '{item.name}': {e_m2m}", exc_info=True)
                            if target_items_to_add: new_m2m_manager.add(*target_items_to_add)

                    # Add default framework if none were copied
                    if hasattr(new_org, 'framework') and not new_org.framework.exists():
                        try:
                            default_framework, _ = SustainAppFramework.objects.get_or_create(
                                name="GRI: With reference to", defaults={"Image": "images/framework/GRI.png"}
                            )
                            new_org.framework.add(default_framework)
                        except Exception as e_df:
                            logger.warning(f"Could not add default framework to org {new_org.name}: {e_df}", exc_info=True)
                self.stdout.write(f"  Finished copying {len(org_map)} organizations.")


                # 3b. Fetch and create Corporates (Corporateentity)
                source_corporates = Corporate.objects.using('source').filter(client=source_client, organization_id__in=org_map.keys())
                self.stdout.write(f"  Found {source_corporates.count()} corporate entities to copy.")
                corporate_map = {}

                for source_corp in source_corporates.iterator():
                    mapped_new_org = org_map.get(source_corp.organization_id)
                    if not mapped_new_org:
                        logger.warning(f"Skipping corporate '{source_corp.name}' (Source ID: {source_corp.id}) as its organization (Source ID: {source_corp.organization_id}) was not mapped.")
                        continue
                    new_corp_data = {
                        field.name: getattr(source_corp, field.name)
                        for field in Corporate._meta.fields if field.name not in ['id', 'client', 'organization']
                    }
                    new_corp = Corporate.objects.create(client=new_client_instance, organization=mapped_new_org, **new_corp_data)
                    corporate_map[source_corp.id] = new_corp
                    # Copy M2M for Corporates (similar to Organizations)
                    m2m_fields_to_copy_corp = ['framework', 'rating', 'certification', 'target', 'regulation']
                    for field_name in m2m_fields_to_copy_corp:
                        if hasattr(source_corp, field_name) and hasattr(new_corp, field_name):
                            source_m2m_manager = getattr(source_corp, field_name)
                            new_m2m_manager = getattr(new_corp, field_name)
                            target_items_to_add = []
                            for item in source_m2m_manager.all():
                                try: target_item = type(item).objects.get(name=item.name); target_items_to_add.append(target_item)
                                except type(item).DoesNotExist: logger.warning(f"M2M Copy for Corp '{new_corp.name}': Could not find matching {field_name} '{item.name}' in target DB.")
                                except Exception as e_m2m_corp: logger.error(f"M2M Copy for Corp '{new_corp.name}': Error finding/adding {field_name} '{item.name}': {e_m2m_corp}", exc_info=True)
                            if target_items_to_add: new_m2m_manager.add(*target_items_to_add)
                self.stdout.write(f"  Finished copying {len(corporate_map)} corporate entities.")


                # 3c. Fetch and create Locations
                source_locations = Location.objects.using('source').filter(client=source_client, corporateentity_id__in=corporate_map.keys())
                self.stdout.write(f"  Found {source_locations.count()} locations to copy.")
                location_map = {}

                for source_loc in source_locations.iterator():
                    mapped_new_corp = corporate_map.get(source_loc.corporateentity_id)
                    if not mapped_new_corp:
                        logger.warning(f"Skipping location '{source_loc.name}' (Source ID: {source_loc.id}) as its corporate entity (ID: {source_loc.corporateentity_id}) was not mapped.")
                        continue
                    new_loc_data = {
                        field.name: getattr(source_loc, field.name)
                        for field in Location._meta.fields if field.name not in ['id', 'client', 'corporateentity']
                    }
                    new_loc = Location.objects.create(client=new_client_instance, corporateentity=mapped_new_corp, **new_loc_data)
                    location_map[source_loc.id] = new_loc
                self.stdout.write(f"  Finished copying {len(location_map)} locations.")


                # 4. Map Paths (DO NOT CREATE NEW ONES IN TARGET)
                self.stdout.write(self.style.MIGRATE_HEADING(f"\nStep 4: Mapping Paths (using only existing paths in target DB for new client '{new_client_instance.name}')"))
                source_raw_responses_path_ids = RawResponse.objects.using('source').filter(client=source_client).values_list('path_id', flat=True).distinct()
                source_paths_qs = Path.objects.using('source').filter(id__in=source_raw_responses_path_ids)

                path_map = {} # Maps source_path.id to existing target_path object
                paths_found_in_target_count = 0
                paths_not_found_in_target_count = 0

                self.stdout.write(f"  Attempting to map {source_paths_qs.count()} unique paths referenced by source RawResponses.")

                for source_path in source_paths_qs.iterator():
                    try:
                        target_path = Path.objects.get(slug=source_path.slug) # Query against default (target) DB
                        path_map[source_path.id] = target_path
                        paths_found_in_target_count +=1
                    except Path.DoesNotExist:
                        paths_not_found_in_target_count +=1
                        logger.warning(f"Path with slug '{source_path.slug}' (Source Path ID: {source_path.id}) NOT FOUND in target database. RawResponses using this path will be skipped.")
                    except Exception as e_path_get:
                        paths_not_found_in_target_count +=1
                        logger.error(f"Error trying to get Path with slug '{source_path.slug}' (Source Path ID: {source_path.id}) from target DB: {e_path_get}", exc_info=True)

                self.stdout.write(f"  Path mapping summary: {paths_found_in_target_count} paths found and mapped in target DB. {paths_not_found_in_target_count} paths from source not found in target DB.")
                if paths_not_found_in_target_count > 0:
                    self.stdout.write(self.style.WARNING(f"  RawResponses associated with the {paths_not_found_in_target_count} unmapped paths will be SKIPPED."))


                # 5. Copy RawResponses
                self.stdout.write(self.style.MIGRATE_HEADING(f"\nStep 5: Copying RawResponses for new client '{new_client_instance.name}'..."))
                source_raw_responses_qs = RawResponse.objects.using('source').filter(client=source_client)
                total_source_rr_count = source_raw_responses_qs.count()
                self.stdout.write(f"  Found {total_source_rr_count} raw responses to potentially copy from source client '{source_client.name}'.")

                failed_rr_save_info = []
                skipped_rr_due_to_missing_path_count = 0
                copied_rr_count = 0
                progress_interval = 1000 # Log progress every 1000 RRs

                for i, source_rr in enumerate(source_raw_responses_qs.iterator()):
                    if (i + 1) % progress_interval == 0:
                        self.stdout.write(f"    Processing RawResponse {i + 1}/{total_source_rr_count}...")

                    target_path_for_rr = path_map.get(source_rr.path_id)
                    if not target_path_for_rr:
                        skipped_rr_due_to_missing_path_count += 1
                        # Optional: logger.info(f"Skipping RawResponse (Source ID: {source_rr.id}) - Its Path (Source ID: {source_rr.path_id}) was not found in target DB.")
                        continue

                    new_organization = org_map.get(source_rr.organization_id) if source_rr.organization_id else None
                    new_corporate = corporate_map.get(source_rr.corporate_id) if source_rr.corporate_id else None
                    new_locale = location_map.get(source_rr.locale_id) if source_rr.locale_id else None

                    # Log if FKs were in source but not mapped (optional detailed logging)
                    # if source_rr.organization_id and not new_organization: logger.debug(...)

                    try:
                        RawResponse.objects.create( # Using create to ensure signals are run
                            data=source_rr.data,
                            path=target_path_for_rr,
                            user=admin_user,
                            client=new_client_instance,
                            organization=new_organization,
                            corporate=new_corporate,
                            locale=new_locale,
                            year=source_rr.year,
                            month=source_rr.month
                            # Add any other fields from source_rr that need to be copied
                        )
                        copied_rr_count += 1
                    except Exception as e_rr_save:
                        error_msg = f"Failed to save RawResponse (Source ID: {source_rr.id}) for new client '{new_client_instance.name}': {e_rr_save}"
                        logger.error(error_msg, exc_info=True)
                        failed_rr_save_info.append({'source_id': source_rr.id, 'error': error_msg})

                self.stdout.write(f"\n  RawResponse Copy Summary for new client '{new_client_instance.name}':")
                self.stdout.write(self.style.SUCCESS(f"    Successfully created {copied_rr_count} RawResponses (signals triggered)."))
                if skipped_rr_due_to_missing_path_count > 0:
                    self.stdout.write(self.style.WARNING(f"    {skipped_rr_due_to_missing_path_count} RawResponses were SKIPPED because their corresponding Paths were not found in the target database."))
                if failed_rr_save_info:
                    self.stdout.write(self.style.ERROR(f"    Encountered save failures with {len(failed_rr_save_info)} RawResponses (these were not due to missing paths):"))
                    for failure in failed_rr_save_info[:5]: # Display first 5 failures in console
                        self.stdout.write(self.style.ERROR(f"      Source RR ID: {failure['source_id']}, Error: {failure['error']}"))
                    if len(failed_rr_save_info) > 5:
                        self.stdout.write(self.style.ERROR(f"      ... and {len(failed_rr_save_info) - 5} more failures (see logs for all details)."))

                total_processed_or_skipped_expectedly = copied_rr_count + skipped_rr_due_to_missing_path_count
                if not failed_rr_save_info and total_processed_or_skipped_expectedly == total_source_rr_count:
                     self.stdout.write(self.style.SUCCESS(f"    All {total_source_rr_count} source RawResponses processed as expected (copied or skipped due to missing paths)."))


            except Exception as e: # Catch any exception during the atomic block
                logger.error(f"An error occurred during the atomic copying process: {e}", exc_info=True)
                client_name_for_error = f"for new client '{new_client_instance.name}' " if new_client_instance else f"for '{new_client_name_generated}' "
                raise CommandError(f"Copying process {client_name_for_error}failed and was rolled back: {e}")

        # Final completion message outside the transaction
        client_name_for_completion = f"for new client '{new_client_instance.name if new_client_instance else new_client_name_generated}'"
        self.stdout.write(self.style.SUCCESS(f'\nData copying process {client_name_for_completion} complete.'))

        # Clean up the dynamically added database connection
        if 'source' in connections.databases:
            del connections.databases['source']
            if 'source' in connections: # Check if alias itself exists in connections wrapper
                 del connections['source']
            self.stdout.write(self.style.SUCCESS("Source database connection configuration removed."))
