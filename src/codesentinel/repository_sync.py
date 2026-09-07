from azure.storage.blob import BlobServiceClient

from codesentinel.github_client import (
    get_repository_file,
    get_repository_tree,
)


REPOSITORY_CONTAINER = "repositories"


def sync_repository_to_blob(
    blob_service_client: BlobServiceClient,
    github_token: str,
    installation_id: int,
    repository_id: int,
    owner: str,
    repo: str,
    branch: str = "main",
) -> int:

    tree = get_repository_tree(
        token=github_token,
        owner=owner,
        repo=repo,
        branch=branch,
    )

    container_client = blob_service_client.get_container_client(
        REPOSITORY_CONTAINER
    )

    uploaded_files = 0

    for item in tree:
        if item.get("type") != "blob":
            continue

        path = item["path"]

        content = get_repository_file(
            token=github_token,
            owner=owner,
            repo=repo,
            path=path,
            branch=branch,
        )

        blob_path = build_blob_path(
            installation_id=installation_id,
            repository_id=repository_id,
            branch=branch,
            path=path,
        )

        blob_client = container_client.get_blob_client(
            blob_path
        )

        blob_client.upload_blob(
            content.encode("utf-8"),
            overwrite=True,
        )

        uploaded_files += 1

    return uploaded_files


def build_blob_path(
    installation_id: int,
    repository_id: int,
    branch: str,
    path: str,
) -> str:

    return (
        f"{installation_id}/"
        f"{repository_id}/"
        f"{branch}/"
        f"{path}"
    )


def update_repository_files(
    blob_service_client: BlobServiceClient,
    github_token: str,
    installation_id: int,
    repository_id: int,
    owner: str,
    repo: str,
    files: list[str],
    branch: str = "main",
) -> int:

    container_client = blob_service_client.get_container_client(
        REPOSITORY_CONTAINER
    )

    updated_files = 0

    for path in files:
        content = get_repository_file(
            token=github_token,
            owner=owner,
            repo=repo,
            path=path,
            branch=branch,
        )

        blob_path = build_blob_path(
            installation_id=installation_id,
            repository_id=repository_id,
            branch=branch,
            path=path,
        )

        blob_client = container_client.get_blob_client(
            blob_path
        )

        blob_client.upload_blob(
            content.encode("utf-8"),
            overwrite=True,
        )

        updated_files += 1

    return updated_files


def delete_repository_files(
    blob_service_client: BlobServiceClient,
    installation_id: int,
    repository_id: int,
    files: list[str],
    branch: str = "main",
) -> int:

    container_client = blob_service_client.get_container_client(
        REPOSITORY_CONTAINER
    )

    deleted_files = 0

    for path in files:
        blob_path = build_blob_path(
            installation_id=installation_id,
            repository_id=repository_id,
            branch=branch,
            path=path,
        )

        blob_client = container_client.get_blob_client(
            blob_path
        )

        blob_client.delete_blob()

        deleted_files += 1

    return deleted_files