import os

from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    AzureOpenAIEmbeddingSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchIndexerIndexProjection,
    SearchIndexerIndexProjectionSelector,
    SearchIndexerSkillset,
    SplitSkill,
)
from dotenv import load_dotenv


load_dotenv()


SKILLSET_NAME = "codesentinel-repository-skillset"

INDEX_NAME = "codesentinel-repository-index"

EMBEDDING_MODEL_NAME = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536


def create_search_indexer_client() -> SearchIndexerClient:
    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]

    credential = DefaultAzureCredential()

    return SearchIndexerClient(
        endpoint=endpoint,
        credential=credential,
    )


def create_repository_skillset() -> SearchIndexerSkillset:
    azure_openai_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    azure_openai_deployment = os.environ[
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
    ]

    split_skill = SplitSkill(
        name="split-repository-content",
        description="Split repository files into smaller chunks for RAG.",
        text_split_mode="pages",
        maximum_page_length=2000,
        page_overlap_length=200,
        context="/document",
        inputs=[
            InputFieldMappingEntry(
                name="text",
                source="/document/content",
            )
        ],
        outputs=[
            OutputFieldMappingEntry(
                name="textItems",
                target_name="chunks",
            )
        ],
    )

    embedding_skill = AzureOpenAIEmbeddingSkill(
        name="generate-code-embeddings",
        description="Generate vector embeddings for repository chunks.",
        context="/document/chunks/*",
        resource_url=azure_openai_endpoint,
        deployment_name=azure_openai_deployment,
        model_name=EMBEDDING_MODEL_NAME,
        dimensions=EMBEDDING_DIMENSIONS,
        inputs=[
            InputFieldMappingEntry(
                name="text",
                source="/document/chunks/*",
            )
        ],
        outputs=[
            OutputFieldMappingEntry(
                name="embedding",
                target_name="content_vector",
            )
        ],
    )

    projection = SearchIndexerIndexProjection(
        selectors=[
            SearchIndexerIndexProjectionSelector(
                target_index_name=INDEX_NAME,
                parent_key_field_name="parent_id",
                source_context="/document/chunks/*",
                mappings=[
                    InputFieldMappingEntry(
                        name="content",
                        source="/document/chunks/*",
                    ),
                    InputFieldMappingEntry(
                        name="content_vector",
                        source="/document/chunks/*/content_vector",
                    ),
                    InputFieldMappingEntry(
                        name="file_path",
                        source="/document/metadata_storage_path",
                    ),
                    InputFieldMappingEntry(
                        name="file_name",
                        source="/document/metadata_storage_name",
                    ),
                ],
            )
        ],
        parameters={
            "projectionMode": "skipIndexingParentDocuments",
        },
    )

    return SearchIndexerSkillset(
        name=SKILLSET_NAME,
        description=(
            "CodeSentinel skillset for splitting repository files "
            "into chunks and generating vector embeddings."
        ),
        skills=[
            split_skill,
            embedding_skill,
        ],
        index_projection=projection,
    )


def create_or_update_repository_skillset() -> None:
    client = create_search_indexer_client()

    skillset = create_repository_skillset()

    result = client.create_or_update_skillset(skillset)

    print(
        f"Search skillset '{result.name}' "
        "updated successfully."
    )


if __name__ == "__main__":
    create_or_update_repository_skillset()