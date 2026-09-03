import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from codesentinel.github_models import PullRequestInfo
from codesentinel.github_auth import create_installation_token
from codesentinel.github_client import get_pull_request_diff
from codesentinel.reviewer import review_code


load_dotenv()

app = FastAPI(title="CodeSentinel V2")

PROJECT_ENDPOINT = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
MODEL_DEPLOYMENT = os.environ["MODEL_DEPLOYMENT"]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()

    pr = PullRequestInfo(
        action=payload["action"],
        installation_id=payload["installation"]["id"],
        repository_owner=payload["repository"]["owner"]["login"],
        repository_name=payload["repository"]["name"],
        pull_request_number=payload["pull_request"]["number"],
        title=payload["pull_request"]["title"],
        description=payload["pull_request"]["body"],
        source_branch=payload["pull_request"]["head"]["ref"],
        target_branch=payload["pull_request"]["base"]["ref"],
        head_sha=payload["pull_request"]["head"]["sha"],
    )

    token = create_installation_token(
        pr.installation_id
    )

    diff = get_pull_request_diff(
        token=token,
        owner=pr.repository_owner,
        repo=pr.repository_name,
        pull_request_number=pr.pull_request_number,
    )

    project = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
    )

    openai = project.get_openai_client()

    review = review_code(
        client=openai,
        model=MODEL_DEPLOYMENT,
        code=diff,
    )

    print("PR Information:")
    print(pr.model_dump_json(indent=2))

    print("\nPR Diff:")
    print(diff)

    print("\nCode Review:")
    print(review.model_dump_json(indent=2))

    return {
        "status": "reviewed",
        "pull_request": pr.model_dump(),
        "review": review.model_dump(),
    }