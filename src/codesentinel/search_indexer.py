import os

from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    FieldMapping,
    IndexingParameters,
    SearchIndexer,
)
from dotenv import load_dotenv


load_dotenv()


INDEXER_NAME = "codesentinel-repository-indexer"
DATA_SOURCE_NAME = "codesentinel-repositories"
SKILLSET_NAME = "codesentinel-repository-skillset"
INDEX_NAME = "codesentinel-repository-index"


def create_search_indexer_client() -> SearchIndexerClient:
    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]

    credential = DefaultAzureCredential()

    return SearchIndexerClient(
        endpoint=endpoint,
        credential=credential,
    )


def create_repository_indexer() -> SearchIndexer:
    return SearchIndexer(
        name=INDEXER_NAME,
        data_source_name=DATA_SOURCE_NAME,
        target_index_name=INDEX_NAME,
        skillset_name=SKILLSET_NAME,
        field_mappings=[
            FieldMapping(
                source_field_name="metadata_storage_path",
                target_field_name="parent_id",
            ),
        ],
        parameters=IndexingParameters(
            configuration={
                "dataToExtract": "contentAndMetadata",
                "parsingMode": "default",
            }
        ),
    )


def create_or_update_repository_indexer() -> None:
    client = create_search_indexer_client()

    indexer = create_repository_indexer()

    result = client.create_or_update_indexer(indexer)

    print(
        f"Search indexer '{result.name}' "
        "created successfully."
    )


if __name__ == "__main__":
    create_or_update_repository_indexer()