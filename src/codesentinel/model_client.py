import os

from agents import set_default_openai_client
from dotenv import load_dotenv
from openai import AsyncOpenAI


load_dotenv()


def configure_azure_openai_client() -> None:
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    api_key = os.environ["AZURE_OPENAI_API_KEY"]

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=f"{endpoint.rstrip('/')}/openai/v1/",
    )

    set_default_openai_client(
        client,
        use_for_tracing=False,
    )