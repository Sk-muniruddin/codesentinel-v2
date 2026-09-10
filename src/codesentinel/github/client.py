import base64

import requests


GITHUB_API_URL = "https://api.github.com"


def get_pull_request_diff(
    token: str,
    owner: str,
    repo: str,
    pull_request_number: int,
) -> str:

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repo}/pulls/{pull_request_number}"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.diff",
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    return response.text


def get_repository_tree(
    token: str,
    owner: str,
    repo: str,
    branch: str = "main",
) -> list[dict]:

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repo}/git/trees/{branch}"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    response = requests.get(
        url,
        headers=headers,
        params={"recursive": "1"},
        timeout=30,
    )

    response.raise_for_status()

    return response.json()["tree"]


def get_repository_file(
    token: str,
    owner: str,
    repo: str,
    path: str,
    branch: str = "main",
) -> str:

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repo}/contents/{path}"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    response = requests.get(
        url,
        headers=headers,
        params={"ref": branch},
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    if data.get("type") != "file":
        raise ValueError(
            f"GitHub path is not a file: {path}"
        )

    content = data.get("content", "")

    return base64.b64decode(content).decode("utf-8")


def create_pull_request_review(
    token: str,
    owner: str,
    repo: str,
    pull_request_number: int,
    body: str,
) -> dict:

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repo}/pulls/"
        f"{pull_request_number}/reviews"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    payload = {
        "body": body,
        "event": "COMMENT",
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()
