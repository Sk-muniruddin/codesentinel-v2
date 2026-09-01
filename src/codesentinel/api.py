from fastapi import FastAPI, Request

from codesentinel.github_models import PullRequestInfo
from codesentinel.github_auth import create_installation_token
from codesentinel.github_client import get_pull_request_diff


app = FastAPI(title="CodeSentinel V2")


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

    print("PR Information:")
    print(pr.model_dump_json(indent=2))

    print("\nPR Diff:")
    print(diff)

    return {
        "status": "received",
        "pull_request": pr.model_dump(),
        "diff": diff,
    }