import os

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv


load_dotenv()


def create_blob_service_client() -> BlobServiceClient:
    account_url = os.environ["AZURE_STORAGE_ACCOUNT_URL"]

    credential = DefaultAzureCredential()

    return BlobServiceClient(
        account_url=account_url,
        credential=credential,
    )