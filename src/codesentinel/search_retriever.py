import os
from dataclasses import dataclass

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


INDEX_NAME = "codesentinel-repository-index"
EMBEDDING_MODEL_NAME = "text-embedding-3-small"
VECTOR_FIELD_NAME = "content_vector"


@dataclass
class RepositoryChunk:
    chunk_id: str
    parent_id: str
    content: str
    file_path: str
    file_name: str


def create_search_client() -> SearchClient:
    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]

    credential = DefaultAzureCredential()

    return SearchClient(
        endpoint=endpoint,
        index_name=INDEX_NAME,
        credential=credential,
    )


def create_openai_client() -> OpenAI:
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default",
    )

    return OpenAI(
        base_url=f"{endpoint.rstrip('/')}/openai/v1/",
        api_key=token_provider,
    )


def create_query_embedding(
    client: OpenAI,
    query: str,
) -> list[float]:
    deployment = os.environ[
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
    ]

    response = client.embeddings.create(
        model=deployment,
        input=query,
    )

    return response.data[0].embedding


def retrieve_repository_context(
    query: str,
    top_k: int = 5,
) -> list[RepositoryChunk]:
    openai_client = create_openai_client()

    query_vector = create_query_embedding(
        openai_client,
        query,
    )

    search_client = create_search_client()

    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=top_k,
        fields=VECTOR_FIELD_NAME,
        exhaustive=True,
    )

    results = search_client.search(
        search_text=None,
        vector_queries=[vector_query],
        select=[
            "chunk_id",
            "parent_id",
            "content",
            "file_path",
            "file_name",
        ],
        top=top_k,
    )

    chunks = []

    for result in results:
        chunks.append(
            RepositoryChunk(
                chunk_id=result["chunk_id"],
                parent_id=result["parent_id"],
                content=result["content"],
                file_path=result["file_path"],
                file_name=result["file_name"],
            )
        )

    return chunks


if __name__ == "__main__":
    query = (
        "How is GitHub repository code synchronized "
        "to Azure Blob Storage?"
    )

    chunks = retrieve_repository_context(
        query=query,
        top_k=3,
    )

    print(f"Retrieved chunks: {len(chunks)}")

    for index, chunk in enumerate(chunks, start=1):
        print(f"\n--- RESULT {index} ---")
        print(f"File: {chunk.file_name}")
        print(f"Path: {chunk.file_path}")
        print(f"Content:\n{chunk.content}")