import os

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from codesentinel.reviewer import review_code


load_dotenv()

PROJECT_ENDPOINT = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
MODEL_DEPLOYMENT = os.environ["MODEL_DEPLOYMENT"]


def main():
    project = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
    )

    openai = project.get_openai_client()

    code = """
def divide(a, b):
    return a / b
"""

    review = review_code(
        openai,
        MODEL_DEPLOYMENT,
        code,
    )

    print(review.model_dump_json(indent=2))


if __name__ == "__main__":
    main()