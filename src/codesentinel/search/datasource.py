import os

from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
)
from dotenv import load_dotenv


load_dotenv()


DATA_SOURCE_NAME = "codesentinel-repositories"
CONTAINER_NAME = "repositories"


def create_search_indexer_client() -> SearchIndexerClient:
    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]

    credential = DefaultAzureCredential()

    return SearchIndexerClient(
        endpoint=endpoint,
        credential=credential,
    )


def create_repository_data_source() -> SearchIndexerDataSourceConnection:
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
    storage_resource_group = os.environ[
        "AZURE_STORAGE_RESOURCE_GROUP"
    ]
    storage_account_name = os.environ[
        "AZURE_STORAGE_ACCOUNT_NAME"
    ]

    resource_id = (
        f"/subscriptions/{subscription_id}"
        f"/resourceGroups/{storage_resource_group}"
        f"/providers/Microsoft.Storage/storageAccounts/"
        f"{storage_account_name}"
    )

    connection_string = f"ResourceId={resource_id};"

    return SearchIndexerDataSourceConnection(
        name=DATA_SOURCE_NAME,
        type="azureblob",
        connection_string=connection_string,
        container=SearchIndexerDataContainer(
            name=CONTAINER_NAME,
        ),
    )


def create_or_update_repository_data_source() -> None:
    client = create_search_indexer_client()

    data_source = create_repository_data_source()

    client.create_or_update_data_source_connection(
        data_source
    )

    print(
        f"Search data source '{DATA_SOURCE_NAME}' "
        "created successfully."
    )


if __name__ == "__main__":
    create_or_update_repository_data_source()