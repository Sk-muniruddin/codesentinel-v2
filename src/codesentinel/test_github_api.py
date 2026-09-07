import os

from dotenv import load_dotenv

from codesentinel.github_auth import create_installation_token
from codesentinel.github_client import (
    get_pull_request_diff,
    get_repository_file,
    get_repository_tree,
)


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

    print("Testing PR diff...")
    diff = get_pull_request_diff(
        token=token,
        owner=owner,
        repo=repo,
        pull_request_number=pull_request_number,
    )

    print("GitHub PR API connection successful.")
    print(f"Diff size: {len(diff)} characters")

    print("\nTesting repository tree...")
    tree = get_repository_tree(
        token=token,
        owner=owner,
        repo=repo,
        branch="main",
    )

    files = [
        item
        for item in tree
        if item.get("type") == "blob"
    ]

    print(f"Repository files found: {len(files)}")

    for item in files[:10]:
        print(f"  {item['path']}")

    if not files:
        print("\nNo files found in repository.")
        return

    test_file = files[0]["path"]

    print(f"\nTesting file retrieval: {test_file}")

    content = get_repository_file(
        token=token,
        owner=owner,
        repo=repo,
        path=test_file,
        branch="main",
    )

    print("File retrieval successful.")
    print(f"File size: {len(content)} characters")

    print("\nGitHub repository retrieval test successful.")


if __name__ == "__main__":
    main()