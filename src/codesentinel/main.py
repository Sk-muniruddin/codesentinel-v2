import os

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from codesentinel.foundry_iq import retrieve_repository_context
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

    retrieval_query = """
Find repository code, functions, classes, tests, configuration,
and dependencies that are relevant to reviewing this pull request.

Pull request diff:

def divide(a, b):
    return a / b
"""

    repository_context = retrieve_repository_context(
        retrieval_query
    )

    print("Repository Context:")
    print(repository_context)

    review = review_code(
        client=openai,
        model=MODEL_DEPLOYMENT,
        code=code,
        repository_context=repository_context,
    )

    print("\nCode Review:")
    print(review.model_dump_json(indent=2))


if __name__ == "__main__":
    main()