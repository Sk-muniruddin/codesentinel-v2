import json
import os

from azure.identity import DefaultAzureCredential
from azure.search.documents.knowledgebases import (
    KnowledgeBaseRetrievalClient,
)
from azure.search.documents.knowledgebases.models import (
    KnowledgeBaseRetrievalRequest,
    KnowledgeRetrievalSemanticIntent,
)
from dotenv import load_dotenv


load_dotenv()


SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
KNOWLEDGE_BASE_NAME = os.environ["FOUNDRY_KNOWLEDGE_BASE_NAME"]


def create_knowledge_base_client() -> KnowledgeBaseRetrievalClient:
    credential = DefaultAzureCredential()

    return KnowledgeBaseRetrievalClient(
        endpoint=SEARCH_ENDPOINT,
        knowledge_base_name=KNOWLEDGE_BASE_NAME,
        credential=credential,
    )


def retrieve_repository_context(
    query: str,
) -> str:
    client = create_knowledge_base_client()

    request = KnowledgeBaseRetrievalRequest(
        intents=[
            KnowledgeRetrievalSemanticIntent(
                search=query,
            )
        ],
    )

    result = client.retrieve(request)

    return _extract_repository_context(result)


def _extract_repository_context(result) -> str:
    if not result.response:
        return ""

    for response_item in result.response:
        if not response_item.content:
            continue

        for content_item in response_item.content:
            text = getattr(content_item, "text", None)

            if not text:
                continue

            try:
                documents = json.loads(text)
            except json.JSONDecodeError:
                continue

            if not isinstance(documents, list):
                continue

            context_parts = []

            for document in documents:
                if not isinstance(document, dict):
                    continue

                title = document.get("title", "unknown")
                content = document.get("content", "")

                if not content:
                    continue

                context_parts.append(
                    f"FILE: {title}\n\n{content}"
                )

            if context_parts:
                return "\n\n---\n\n".join(context_parts)

    return ""