import os

from dotenv import load_dotenv

from codesentinel.blob_storage import create_blob_service_client
from codesentinel.github_auth import create_installation_token
from codesentinel.repository_sync import sync_repository_to_blob


load_dotenv()


def main():
    installation_id = int(
        os.environ["GITHUB_INSTALLATION_ID"]
    )

    repository_id = int(
        os.environ["GITHUB_TEST_REPOSITORY_ID"]
    )

    owner = os.environ["GITHUB_TEST_REPO_OWNER"]
    repo = os.environ["GITHUB_TEST_REPO_NAME"]

    token = create_installation_token(
        installation_id
    )

    blob_service_client = create_blob_service_client()

    uploaded_files = sync_repository_to_blob(
        blob_service_client=blob_service_client,
        github_token=token,
        installation_id=installation_id,
        repository_id=repository_id,
        owner=owner,
        repo=repo,
        branch="main",
    )

    print(
        f"Repository sync successful. "
        f"Uploaded files: {uploaded_files}"
    )


if __name__ == "__main__":
    main()