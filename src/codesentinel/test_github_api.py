import os

from dotenv import load_dotenv

from codesentinel.github_auth import create_installation_token
from codesentinel.github_client import get_pull_request_diff


load_dotenv()


def main():
    installation_id = int(
        os.environ["GITHUB_INSTALLATION_ID"]
    )

    owner = os.environ["GITHUB_TEST_REPO_OWNER"]
    repo = os.environ["GITHUB_TEST_REPO_NAME"]
    pull_request_number = int(
        os.environ["GITHUB_TEST_PR_NUMBER"]
    )

    token = create_installation_token(
        installation_id
    )

    diff = get_pull_request_diff(
        token=token,
        owner=owner,
        repo=repo,
        pull_request_number=pull_request_number,
    )

    print("GitHub API connection successful.")
    print("\nPR Diff:")
    print(diff)


if __name__ == "__main__":
    main()