from fastapi import FastAPI, Request
from dotenv import load_dotenv

from codesentinel.blob_storage import create_blob_service_client
from codesentinel.foundry_iq import retrieve_repository_context
from codesentinel.github_models import (
    PullRequestInfo,
    RepositoryPushInfo,
)
from codesentinel.github_auth import create_installation_token
from codesentinel.github_client import get_pull_request_diff
from codesentinel.repository_sync import (
    delete_repository_files,
    sync_repository_to_blob,
    update_repository_files,
)
from codesentinel.runner import run_code_review


load_dotenv()


app = FastAPI(title="CodeSentinel V2")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()

    event_type = request.headers.get("X-GitHub-Event")

    if event_type == "installation":
        return await handle_installation_event(payload)

    if event_type == "push":
        return await handle_push_event(payload)

    if event_type == "pull_request":
        return await handle_pull_request_event(payload)

    return {
        "status": "ignored",
        "event": event_type,
    }


async def handle_installation_event(
    payload: dict,
):
    action = payload.get("action")

    if action != "created":
        return {
            "status": "ignored",
            "event": "installation",
            "action": action,
        }

    installation = payload["installation"]

    installation_id = installation["id"]

    repositories = payload.get(
        "repositories",
        []
    )

    if not repositories:
        return {
            "status": "synchronized",
            "event": "installation",
            "action": action,
            "installation_id": installation_id,
            "repositories": 0,
            "uploaded_files": 0,
        }

    token = create_installation_token(
        installation_id
    )

    blob_service_client = create_blob_service_client()

    repository_results = []

    for repository in repositories:
        repository_id = repository["id"]
        repository_name = repository["name"]
        repository_owner = repository["owner"]["login"]

        uploaded_files = sync_repository_to_blob(
            blob_service_client=blob_service_client,
            github_token=token,
            installation_id=installation_id,
            repository_id=repository_id,
            owner=repository_owner,
            repo=repository_name,
            branch="main",
        )

        repository_results.append(
            {
                "repository_id": repository_id,
                "repository": repository_name,
                "uploaded_files": uploaded_files,
            }
        )

    print("GitHub App installation synchronization:")
    print(f"Installation ID: {installation_id}")
    print(
        f"Repositories synchronized: "
        f"{len(repository_results)}"
    )

    return {
        "status": "synchronized",
        "event": "installation",
        "action": action,
        "installation_id": installation_id,
        "repositories": repository_results,
    }


async def handle_push_event(
    payload: dict,
):
    if "installation" not in payload:
        return {
            "status": "ignored",
            "reason": "missing installation information",
        }

    repository = payload["repository"]

    branch = payload["ref"].removeprefix(
        "refs/heads/"
    )

    if branch != "main":
        return {
            "status": "ignored",
            "reason": "push was not to main",
            "branch": branch,
        }

    added_files = []
    modified_files = []
    removed_files = []

    for commit in payload.get("commits", []):
        added_files.extend(
            commit.get("added", [])
        )

        modified_files.extend(
            commit.get("modified", [])
        )

        removed_files.extend(
            commit.get("removed", [])
        )

    push = RepositoryPushInfo(
        installation_id=payload["installation"]["id"],
        repository_id=repository["id"],
        repository_owner=repository["owner"]["login"],
        repository_name=repository["name"],
        branch=branch,
        before_sha=payload["before"],
        after_sha=payload["after"],
        added=added_files,
        modified=modified_files,
        removed=removed_files,
    )

    token = create_installation_token(
        push.installation_id
    )

    blob_service_client = create_blob_service_client()

    files_to_update = [
        *push.added,
        *push.modified,
    ]

    updated_files = update_repository_files(
        blob_service_client=blob_service_client,
        github_token=token,
        installation_id=push.installation_id,
        repository_id=push.repository_id,
        owner=push.repository_owner,
        repo=push.repository_name,
        files=files_to_update,
        branch=push.branch,
    )

    deleted_files = delete_repository_files(
        blob_service_client=blob_service_client,
        installation_id=push.installation_id,
        repository_id=push.repository_id,
        files=push.removed,
        branch=push.branch,
    )

    print("Repository push synchronization:")
    print(push.model_dump_json(indent=2))

    print(f"Updated files: {updated_files}")
    print(f"Deleted files: {deleted_files}")

    return {
        "status": "synchronized",
        "event": "push",
        "repository": push.repository_name,
        "branch": push.branch,
        "updated_files": updated_files,
        "deleted_files": deleted_files,
        "before_sha": push.before_sha,
        "after_sha": push.after_sha,
    }


async def handle_pull_request_event(
    payload: dict,
):
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

    # Retrieve repository knowledge before running the Agent.
    retrieval_query = f"""
Find repository code, functions, classes, tests, configuration,
interfaces, and dependencies that are directly relevant to
reviewing this GitHub pull request.

Prioritize files related to the files and code changed by the PR.

Pull request diff:

{diff}
"""

    repository_context = retrieve_repository_context(
        retrieval_query
    )

    # Build the complete input that will be given to the Agent.
    review_input = f"""
Review this GitHub Pull Request.

====================
PULL REQUEST
====================

Repository:
{pr.repository_owner}/{pr.repository_name}

Pull Request:
#{pr.pull_request_number}

Title:
{pr.title}

Description:
{pr.description or ""}

====================
PULL REQUEST DIFF
====================

{diff}

====================
REPOSITORY KNOWLEDGE
====================

{repository_context}

====================
REVIEW REQUIREMENTS
====================

Use the repository knowledge to understand the existing
implementation before reviewing the Pull Request.

The Pull Request diff is the code being reviewed.

The repository knowledge is reference context and is not
part of the Pull Request.

Return the final review using the required CodeReview structure.
"""

    # Runner executes the CodeSentinel Agent.
    review = await run_code_review(
        review_input
    )

    print("PR Information:")
    print(pr.model_dump_json(indent=2))

    print("\nPR Diff:")
    print(diff)

    print("\nRepository Context:")
    print(repository_context)

    print("\nCode Review:")
    print(review.model_dump_json(indent=2))

    return {
        "status": "reviewed",
        "pull_request": pr.model_dump(),
        "review": review.model_dump(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "codesentinel.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )