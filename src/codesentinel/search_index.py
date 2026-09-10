import os

from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    HnswParameters,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchableField,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from dotenv import load_dotenv


load_dotenv()


INDEX_NAME = "codesentinel-repository-index"

VECTOR_PROFILE_NAME = "codesentinel-vector-profile"
VECTOR_ALGORITHM_NAME = "codesentinel-hnsw"

EMBEDDING_DIMENSIONS = 1536


def create_search_index_client() -> SearchIndexClient:
    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]

    credential = DefaultAzureCredential()

    return SearchIndexClient(
        endpoint=endpoint,
        credential=credential,
    )


def create_repository_index() -> SearchIndex:
    fields = [
        SimpleField(
            name="chunk_id",
            type=SearchFieldDataType.String,
            key=True,
            filterable=True,
            sortable=True,
        ),
        SimpleField(
            name="parent_id",
            type=SearchFieldDataType.String,
            filterable=True,
        ),
        SearchableField(
            name="content",
            type=SearchFieldDataType.String,
        ),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(
                SearchFieldDataType.Single
            ),
            searchable=True,
            vector_search_dimensions=EMBEDDING_DIMENSIONS,
            vector_search_profile_name=VECTOR_PROFILE_NAME,
        ),
        SimpleField(
            name="file_path",
            type=SearchFieldDataType.String,
            filterable=True,
            sortable=True,
        ),
        SearchableField(
            name="file_name",
            type=SearchFieldDataType.String,
            filterable=True,
        ),
        SimpleField(
            name="language",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),
        SimpleField(
            name="repository",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),
        SimpleField(
            name="branch",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),
        SimpleField(
            name="commit_sha",
            type=SearchFieldDataType.String,
            filterable=True,
        ),
        SimpleField(
            name="blob_path",
            type=SearchFieldDataType.String,
            filterable=True,
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name=VECTOR_ALGORITHM_NAME,
                parameters=HnswParameters(
                    metric="cosine",
                ),
            )
        ],
        profiles=[
            VectorSearchProfile(
                name=VECTOR_PROFILE_NAME,
                algorithm_configuration_name=VECTOR_ALGORITHM_NAME,
            )
        ],
    )

    semantic_configuration = SemanticConfiguration(
        name="codesentinel-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(
                field_name="file_name"
            ),
            content_fields=[
                SemanticField(
                    field_name="content"
                )
            ],
        ),
    )

    semantic_search = SemanticSearch(
        configurations=[semantic_configuration]
    )

    return SearchIndex(
        name=INDEX_NAME,
        description=(
            "CodeSentinel repository knowledge index containing "
            "repository code chunks, metadata, and vector embeddings "
            "for pull request context retrieval."
        ),
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search,
    )


def create_or_update_repository_index() -> None:
    client = create_search_index_client()

    index = create_repository_index()

    result = client.create_or_update_index(index)

    print(
        f"Search index '{result.name}' "
        "created successfully."
    )


if __name__ == "__main__":
    create_or_update_repository_index()