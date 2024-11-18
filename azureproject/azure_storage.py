from storages.backends.azure_storage import AzureStorage
import os


class AzureMediaStorage(AzureStorage):
    account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", None)
    account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY", None)
    azure_container = "media"
    expiration_secs = None


class AzureStaticStorage(AzureStorage):
    account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", None)
    account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY", None)
    azure_container = "static"
    expiration_secs = None
