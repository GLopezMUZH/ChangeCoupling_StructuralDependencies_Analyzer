from datetime import datetime
from typing import Generator, List

from .domain.commit import Commit


class Repository:
    def __init__(
        self, path_to_repo: str | List[str],
        single: str = ...,
        since: datetime = ...,
        to: datetime = ...,
        from_commit: str = ...,
        to_commit: str = ...,
        from_tag: str = ...,
        to_tag: str = ...,
        include_refs: bool = ...,
        include_remotes: bool = ...,
        num_workers: int = 1,
        only_in_branch: str = ...,
        only_modifications_with_file_types: List[str] = ...,
        only_no_merge: bool = ...,
        only_authors: List[str] = ...,
        only_commits: List[str] = ...,
        only_releases: bool = ...,
        filepath: str = ...,
        include_deleted_files: bool = ...,
        histogram_diff: bool = ...,
        skip_whitespaces: bool = ...,
        clone_repo_to: str = ...,
        order: str = ...,
    ) -> None: ...

    def traverse_commits(self) -> Generator[Commit, None, None]: ...
