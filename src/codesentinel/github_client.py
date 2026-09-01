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