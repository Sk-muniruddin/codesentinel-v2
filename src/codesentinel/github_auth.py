import os
import time

import jwt
import requests


GITHUB_API_URL = "https://api.github.com"


def create_app_jwt() -> str:
    app_id = os.environ["GITHUB_APP_ID"]
    private_key = os.environ["GITHUB_PRIVATE_KEY"]

    now = int(time.time())

    payload = {
        "iat": now - 60,
        "exp": now + (10 * 60),
        "iss": app_id,
    }

    return jwt.encode(
        payload,
        private_key,
        algorithm="RS256",
    )


def create_installation_token(installation_id: int) -> str:
    app_jwt = create_app_jwt()

    url = (
        f"{GITHUB_API_URL}/app/installations/"
        f"{installation_id}/access_tokens"
    )

    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
    }

    response = requests.post(
        url,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()["token"]