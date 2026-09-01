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