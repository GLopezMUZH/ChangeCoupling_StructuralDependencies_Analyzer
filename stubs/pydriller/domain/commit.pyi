from enum import Enum
from datetime import datetime
from typing import Optional, List

from .developer import Developer


class ModificationType(Enum):
    ADD = ...
    COPY = ...
    RENAME = ...
    DELETE = ...
    MODIFY = ...
    UNKNOWN = ...


class Method:
    name: str
    long_name: str
    parameters: List[str]
    nloc: int


class ModifiedFile:
    filename: str
    old_path: Optional[str]
    new_path: Optional[str]
    methods: List[Method]
    methods_before: List[Method]
    changed_methods: List[Method]
    change_type: ModificationType
    source_code: str
    source_code_before: str


class Commit:
    hash: str
    committer_date: datetime
    author: Developer
    merge: bool
    modified_files: List[ModifiedFile]
    deletions: int
    insertions: int
    lines: int
