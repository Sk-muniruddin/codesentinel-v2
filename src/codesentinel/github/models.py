from pydantic import BaseModel


class PullRequestInfo(BaseModel):
    action: str
    installation_id: int
    repository_owner: str
    repository_name: str
    pull_request_number: int
    title: str
    description: str | None
    source_branch: str
    target_branch: str
    head_sha: str


class RepositoryPushInfo(BaseModel):
    installation_id: int
    repository_id: int
    repository_owner: str
    repository_name: str
    branch: str
    before_sha: str
    after_sha: str
    added: list[str]
    modified: list[str]
    removed: list[str]