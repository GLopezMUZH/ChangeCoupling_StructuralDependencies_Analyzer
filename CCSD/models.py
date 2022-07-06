# pylint: disable=too-many-instance-attributes,too-many-arguments

# %%
import os
from datetime import datetime
from enum import Enum
from typing import NamedTuple, Optional, List, TypedDict


class ActionClass(Enum):
    ADD = 1
    DELETE = 2
    INSERT = 3
    MOVE = 4
    MODIFIY = 5


_PATH_TO_SRC_COMPACT_XML_PARSING = os.path.normpath(
    "../resources/astChangeAnalyzer_0_1_parsexmlcompact.jar"
)
_PATH_TO_SRC_DIFF_JAR = {
    "cpp": os.path.normpath("../resources/astChangeAnalyzer_0_1_cpp.jar"),
    "java": os.path.normpath("../resources/astChangeAnalyzer_0_1_java.jar"),
}
_DEFAULT_COMMIT_FILE_TYPES = {
    "cpp": [".cpp"],
    "java": [".java"],
}

ProjectConfig = TypedDict(
    "ProjectConfig",
    {
        "proj_name": str,
        "proj_lang": str,
        "commit_file_types": List[str],
        "repo_url": str,
        "repo_type": str,
        "start_repo_date": Optional[datetime],
        "end_repo_date": Optional[datetime],
        "repo_from_tag": Optional[str],
        "repo_to_tag": Optional[str],
        "repo_from_commit": Optional[str],
        "repo_to_commit": Optional[str],
        "save_cache_files": Optional[bool],
        "delete_cache_files": Optional[bool],
        "only_in_branch": str,
        "path_to_src_compact_xml_parsing": str,
        "path_to_src_diff_jar": str,
    },
)


def build_project_config(
    proj_name: str,
    proj_lang: str,
    repo_url: str,
    commit_file_types: Optional[List[str]] = None,
    repo_type: str = "Git",
    start_repo_date: Optional[datetime] = None,
    end_repo_date: Optional[datetime] = None,
    repo_from_tag: Optional[str] = None,
    repo_to_tag: Optional[str] = None,
    repo_from_commit: Optional[str] = None,
    repo_to_commit: Optional[str] = None,
    save_cache_files: Optional[bool] = True,
    delete_cache_files: Optional[bool] = True,
    only_in_branch: Optional[str] = None,
) -> ProjectConfig:
    if proj_lang not in _DEFAULT_COMMIT_FILE_TYPES:
        raise Exception(f"invalid language {proj_lang}")
    return ProjectConfig(
        proj_name=proj_name,
        proj_lang=proj_lang,
        commit_file_types=commit_file_types or _DEFAULT_COMMIT_FILE_TYPES[proj_lang],
        repo_url=repo_url,
        repo_type=repo_type,
        start_repo_date=start_repo_date,
        end_repo_date=end_repo_date,
        repo_from_tag=repo_from_tag,
        repo_to_tag=repo_to_tag,
        repo_from_commit=repo_from_commit,
        repo_to_commit=repo_to_commit,
        save_cache_files=save_cache_files,
        delete_cache_files=delete_cache_files,
        only_in_branch=only_in_branch or "master",
        path_to_src_compact_xml_parsing=_PATH_TO_SRC_COMPACT_XML_PARSING,
        path_to_src_diff_jar=_PATH_TO_SRC_DIFF_JAR[proj_lang],
    )


ProjectPaths = TypedDict(
    "ProjectPaths",
    {
        "path_to_proj_data_dir": str,
        "path_to_src_files": str,
        "str_path_to_src_files": str,
        "path_to_project_db": str,
        "path_to_edge_hist_db": str,
        "path_to_cache_dir": str,
        "path_to_cache_current": str,
        "path_to_cache_previous": str,
        "path_to_cache_sourcediff": str,
        "path_to_cache_src_dir": str,
    },
)


def build_project_paths(
    proj_name: str, path_to_proj_data_dir: str, path_to_src_files: str = "../src-code/"
) -> ProjectPaths:
    print("build_project_paths, curr dir", os.getcwd())
    cache_dir = os.path.join(path_to_proj_data_dir, proj_name, ".cache")
    paths = ProjectPaths(
        # project data directory
        path_to_proj_data_dir=os.path.join(path_to_proj_data_dir, proj_name),
        # for finding path from package
        path_to_src_files=os.path.normpath(path_to_src_files),
        # for replacing paths on the cg db
        str_path_to_src_files=path_to_src_files,
        # analytics database
        path_to_project_db=os.path.join(
            path_to_proj_data_dir, proj_name, proj_name + "_analytics.db"
        ),
        # edge_hist database
        path_to_edge_hist_db=os.path.join(
            path_to_proj_data_dir, proj_name, proj_name + "_edge_hist.db"
        ),
        # CACHE FILES
        # temporary files main folder
        path_to_cache_dir=cache_dir,
        # ast parsing analytics
        path_to_cache_current=os.path.join(cache_dir, "astparsing", "current"),
        path_to_cache_previous=os.path.join(cache_dir, "astparsing", "previous"),
        path_to_cache_sourcediff=os.path.join(cache_dir, "astparsing", "sourcediff"),
        # cache source to track git changes
        path_to_cache_src_dir=os.path.join(cache_dir, "git"),
    )

    for path in [
        paths["path_to_cache_dir"],
        paths["path_to_cache_current"],
        paths["path_to_cache_previous"],
        paths["path_to_cache_sourcediff"],
        paths["path_to_cache_src_dir"],
    ]:
        print(path)
        print("exists: ", os.path.exists(path))
        if not os.path.exists(path):
            os.makedirs(path)
        print("exists: ", os.path.exists(path))

    return paths


class FileData:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        # calculate dir path and file name
        self.file_dir_path = os.path.dirname(file_path)
        self.file_name = os.path.basename(file_path)

    def get_file_name(self) -> str:
        return self.file_name

    def get_file_dir_path(self) -> str:
        return self.file_dir_path

    def get_file_path(self) -> str:
        return self.file_path

    def __str__(self) -> str:
        return f"FileData [file_name: {self.file_name}, file_dir_path: {self.file_dir_path}]"


class GitCommitInfo:
    def __init__(
        self,
        commit_hash: Optional[str] = None,
        commit_commiter_datetime: Optional[str] = None,
        author: Optional[str] = None,
        in_main_branch: Optional[bool] = None,
        merge: Optional[bool] = None,
        nr_modified_files: Optional[int] = None,
        nr_deletions: Optional[int] = None,
        nr_insertions: Optional[int] = None,
        nr_lines: Optional[int] = None,
    ) -> None:
        """
        A CallCommitInfo represents the relationship between a function in a file
        and one of the functions it calls within. There can be many CCI pro file and
        function, if it calls several others. Based in the FileImport data the source
        of the called function can be inferred.
        """
        self.commit_hash = commit_hash
        self.commit_commiter_datetime = commit_commiter_datetime
        self.author = author
        self.in_main_branch = in_main_branch
        self.merge = merge
        self.nr_modified_files = nr_modified_files
        self.nr_deletions = nr_deletions
        self.nr_insertions = nr_insertions
        self.nr_lines = nr_lines

    def __str__(self) -> str:
        return (
            f"GitCommitInfo: commit_hash: {self.commit_hash}, commit_commiter_datetime: {self.commit_commiter_datetime}, "
            f"nr_modified_files: {self.nr_modified_files}"
        )


class FileCommitInfo:
    def __init__(
        self,
        src_file_data: FileData,
        commit_hash: Optional[str] = None,
        commit_commiter_datetime: Optional[str] = None,
        commit_file_name: Optional[str] = None,
        commit_new_path: Optional[str] = None,
        commit_old_path: Optional[str] = None,
        change_type: Optional[bool] = None,
    ) -> None:
        """
        A CallCommitInfo represents the relationship between a function in a file
        and one of the functions it calls within. There can be many CCI pro file and
        function, if it calls several others. Based in the FileImport data the source
        of the called function can be inferred.
        """
        self.file_name = src_file_data.file_name
        self.file_dir_path = src_file_data.file_dir_path
        self.file_path = src_file_data.file_path
        self.commit_hash = commit_hash
        self.commit_commiter_datetime = commit_commiter_datetime
        self.commit_file_name = commit_file_name
        self.commit_new_path = commit_new_path
        self.commit_old_path = commit_old_path
        self.change_type = change_type
        self.path_change = commit_new_path != commit_old_path

    def __str__(self) -> str:
        return (
            f"FileCommitInfo: file_name: {self.file_name}, commit_file_name: {self.commit_file_name}, "
            f"commit_commiter_datetime: {self.commit_commiter_datetime}, change_type: {self.change_type}, path_change: {self.path_change}"
        )


class FunctionCommitInfo:
    def __init__(
        self,
        src_file_data: FileData,
        function_name: Optional[str] = None,
        function_long_name: Optional[str] = None,
        function_parameters: Optional[str] = None,
        function_nloc: Optional[str] = None,
        commit_hash: Optional[str] = None,
        commit_commiter_datetime: Optional[str] = None,
        commit_file_name: Optional[str] = None,
        commit_new_path: Optional[str] = None,
        commit_old_path: Optional[str] = None,
    ) -> None:
        """
        A CallCommitInfo represents the relationship between a function in a file
        and one of the functions it calls within. There can be many CCI pro file and
        function, if it calls several others. Based in the FileImport data the source
        of the called function can be inferred.
        """
        self.file_name = src_file_data.file_name
        self.file_dir_path = src_file_data.file_dir_path
        self.file_path = src_file_data.file_path
        self.function_name = function_name
        self.function_long_name = function_long_name
        self.function_parameters = function_parameters
        self.function_nloc = function_nloc
        self.commit_hash = commit_hash
        self.commit_commiter_datetime = commit_commiter_datetime
        self.commit_file_name = commit_file_name
        self.commit_new_path = commit_new_path
        self.commit_old_path = commit_old_path
        self.path_change = commit_new_path != commit_old_path

    def __str__(self) -> str:
        return (
            f"FunctionCommitInfo: function_name: {self.function_name}, file_name: {self.file_name}, "
            f"commit_commiter_datetime: {self.commit_commiter_datetime}, commit_hash: {self.commit_hash}, path_change: {self.path_change}"
        )


class CallCommitInfo:
    def __init__(
        self,
        src_file_data: FileData,
        calling_function: str,
        called_function: str,
        action_class: ActionClass,
        commit_hash_start: Optional[str] = None,
        commit_start_datetime: Optional[str] = None,
        commit_hash_end: Optional[str] = None,
        commit_end_datetime: Optional[str] = None,
    ) -> None:
        """
        A CallCommitInfo represents the relationship between a function in a file
        and one of the functions it calls within. There can be many CCI pro file and
        function, if it calls several others. Based in the FileImport data the source
        of the called function can be inferred.
        """
        self.file_name = src_file_data.file_name
        self.file_dir_path = src_file_data.file_dir_path
        self.file_path = src_file_data.file_path
        self.calling_function = calling_function
        self.called_function = called_function
        self.action_class = action_class
        self.commit_hash_start = commit_hash_start
        self.commit_start_datetime = commit_start_datetime
        self.commit_hash_end = commit_hash_end
        self.commit_end_datetime = commit_end_datetime

    def get_file_name(self) -> str:
        return self.file_name

    def get_file_dir_path(self) -> str:
        return self.file_dir_path

    def get_file_path(self) -> str:
        return self.file_path

    def get_calling_function(self) -> str:
        return self.calling_function

    def get_called_function(self) -> str:
        return self.called_function

    def get_action_class(self) -> ActionClass:
        return self.action_class

    def get_commit_hash_start(self) -> Optional[str]:
        return self.commit_hash_start

    def get_commit_start_datetime(self) -> Optional[str]:
        return self.commit_start_datetime

    def get_commit_hash_end(self) -> Optional[str]:
        return self.commit_hash_end

    def get_commit_end_datetime(self) -> Optional[str]:
        return self.commit_end_datetime

    def set_commit_hash_start(self, commit_hash_start: Optional[str]) -> None:
        self.commit_hash_start = commit_hash_start

    def set_commit_start_datetime(self, commit_start_datetime: Optional[str]) -> None:
        self.commit_start_datetime = commit_start_datetime

    def set_commit_hash_end(self, commit_hash_end: Optional[str]) -> None:
        self.commit_hash_end = commit_hash_end

    def set_commit_end_datetime(self, commit_end_datetime: Optional[str]) -> None:
        self.commit_end_datetime = commit_end_datetime

    def __str__(self) -> str:
        return (
            f"CallCommitInfo: source_node: {self.calling_function}, called_function: {self.called_function}, "
            f"start_date: {self.commit_start_datetime}, end_date: {self.commit_end_datetime}, file_path: {self.file_path}"
        )


class FunctionToFile:
    def __init__(
        self,
        src_file_data: FileData,
        function_name: Optional[str] = None,
        function_long_name: Optional[str] = None,
        function_parameters: Optional[str] = None,
        commit_hash_start: Optional[str] = None,
        commit_start_datetime: Optional[str] = None,
        commit_hash_end: Optional[str] = None,
        commit_end_datetime: Optional[str] = None,
    ) -> None:
        """
        A CallCommitInfo represents the relationship between a function in a file
        and one of the functions it calls within. There can be many CCI pro file and
        function, if it calls several others. Based in the FileImport data the source
        of the called function can be inferred.
        """
        self.file_name = src_file_data.file_name
        self.file_dir_path = src_file_data.file_dir_path
        self.file_path = src_file_data.file_path
        self.function_name = function_name
        self.function_long_name = function_long_name
        self.function_parameters = function_parameters
        self.commit_hash_start = commit_hash_start
        self.commit_start_datetime = commit_start_datetime
        self.commit_hash_end = commit_hash_end
        self.commit_end_datetime = commit_end_datetime

    def set_commit_hash_start(self, commit_hash_start: Optional[str]) -> None:
        self.commit_hash_start = commit_hash_start

    def set_commit_start_datetime(self, commit_start_datetime: Optional[str]) -> None:
        self.commit_start_datetime = commit_start_datetime

    def set_commit_hash_end(self, commit_hash_end: Optional[str]) -> None:
        self.commit_hash_end = commit_hash_end

    def set_commit_end_datetime(self, commit_end_datetime: Optional[str]) -> None:
        self.commit_end_datetime = commit_end_datetime

    def __str__(self) -> str:
        return (
            f"FunctionToFile: file_name: {self.file_name}, function_name: {self.function_name}, file_path: {self.file_path}, "
            f"commit_start_datetime: {self.commit_start_datetime}, commit_end_datetime: {self.commit_end_datetime}"
        )


class FileImport:
    def __init__(
        self,
        src_file_data: FileData,
        import_file_path: str,
        import_file_name: str,
        import_file_dir_path: str,
        import_file_pkg: Optional[str] = None,
        commit_hash_start: Optional[str] = None,
        commit_start_datetime: Optional[str] = None,
        commit_hash_end: Optional[str] = None,
        commit_end_datetime: Optional[str] = None,
    ) -> None:
        self.file_name = src_file_data.file_name
        self.file_dir_path = src_file_data.file_dir_path
        self.file_path = src_file_data.file_path
        self.import_file_path = import_file_path
        self.import_file_name = import_file_name
        self.import_file_dir_path = import_file_dir_path
        self.import_file_pkg = import_file_pkg
        self.commit_hash_start = commit_hash_start
        self.commit_start_datetime = commit_start_datetime
        self.commit_hash_end = commit_hash_end
        self.commit_end_datetime = commit_end_datetime

    def get_file_name(self) -> str:
        return self.file_name

    def get_file_dir_path(self) -> str:
        return self.file_dir_path

    def get_file_path(self) -> str:
        return self.file_path

    def get_import_file_path(self) -> str:
        return self.import_file_path

    def get_import_file_name(self) -> str:
        return self.import_file_name

    def get_import_file_dir_path(self) -> str:
        return self.import_file_dir_path

    def get_import_file_pkg(self) -> Optional[str]:
        return self.import_file_pkg

    def get_commit_hash_start(self) -> Optional[str]:
        return self.commit_hash_start

    def get_commit_start_datetime(self) -> Optional[str]:
        return self.commit_start_datetime

    def get_commit_hash_end(self) -> Optional[str]:
        return self.commit_hash_end

    def get_commit_end_datetime(self) -> Optional[str]:
        return self.commit_end_datetime

    def set_commit_hash_end(self, commit_hash_end: Optional[str]) -> None:
        self.commit_hash_end = commit_hash_end

    def set_commit_end_datetime(self, commit_end_datetime: Optional[str]) -> None:
        self.commit_end_datetime = commit_end_datetime

    def __str__(self) -> str:
        return (
            f"FileImport[src_file_path: {self.file_path}, import_file_name: {self.import_file_name}, "
            f"import_file_dir_path: {self.import_file_dir_path}, import_file_pkg: {self.import_file_pkg}]"
        )


class CommitDates:
    def __init__(self, commit_hash: str, commiter_datetime: datetime) -> None:
        self.commit_hash = commit_hash
        self.commiter_datetime = commiter_datetime

    def get_commit_hash(self) -> str:
        return self.commit_hash

    def get_commiter_datetime(self) -> datetime:
        return self.commiter_datetime


class CommitPairDates:
    def __init__(
        self,
        commit_hash_start: str,
        commit_start_datetime: str,
        commit_hash_end: str,
        commit_end_datetime: str,
    ) -> None:
        self.commit_hash_start = commit_hash_start
        self.commit_start_datetime = commit_start_datetime
        self.commit_hash_end = commit_hash_end
        self.commit_end_datetime = commit_end_datetime

    def get_commit_hash_start(self) -> str:
        return self.commit_hash_start

    def get_commit_start_datetime(self) -> str:
        return self.commit_start_datetime

    def get_commit_hash_end(self) -> str:
        return self.commit_hash_end

    def get_commit_end_datetime(self) -> str:
        return self.commit_end_datetime


# %%
EdgeType = {
    0: "EDGE_UNDEFINED",
    1: "EDGE_MEMBER",
    2: "EDGE_TYPE_USAGE",
    4: "EDGE_USAGE",
    8: "EDGE_CALL",
    16: "EDGE_INHERITANCE",
    32: "EDGE_OVERRIDE",
    64: "EDGE_TYPE_ARGUMENT",
    128: "EDGE_TEMPLATE_SPECIALIZATION",
    256: "EDGE_INCLUDE",
    512: "EDGE_IMPORT",
    1024: "EDGE_BUNDLED_EDGES",
    2048: "EDGE_MACRO_USAGE",
    4096: "EDGE_ANNOTATION_USAGE",
}

NodeType = {
    1: "NODE_SYMBOL",
    2: "NODE_TYPE",
    4: "NODE_BUILTIN_TYPE",
    8: "NODE_MODULE",
    16: "NODE_NAMESPACE",
    32: "NODE_PACKAGE",
    64: "NODE_STRUCT",
    128: "NODE_CLASS",
    256: "NODE_INTERFACE",
    512: "NODE_ANNOTATION",
    1024: "NODE_GLOBAL_VARIABLE",
    2048: "NODE_FIELD",
    4096: "NODE_FUNCTION",
    8192: "NODE_METHOD",
    16384: "NODE_ENUM",
    32768: "NODE_ENUM_CONSTANT",
    65536: "NODE_TYPEDEF",
    131072: "NODE_TYPE_PARAMETER",
    262144: "NODE_FILE",
    524288: "NODE_MACRO",
    1048576: "NODE_UNION",
}

FunctionCall = NamedTuple(
    "FunctionCall",
    [
        ("calling_function_unqualified_name", str),
        ("calling_function_nr_parameters", str),
        ("called_function_unqualified_name", str),
    ],
)

ExtendedFunctionCall = NamedTuple(
    "ExtendedFunctionCall",
    [
        ("calling_function_unqualified_name", str),
        ("calling_function_nr_parameters", str),
        ("called_function_unqualified_name", str),
        ("commit_hash_start", Optional[str]),
        ("commit_start_datetime", Optional[datetime]),
        ("commit_hash_oldest", str),
        ("commit_oldest_datetime", datetime),
        ("commit_hash_end", Optional[str]),
        ("commit_end_datetime", Optional[datetime]),
        ("closed", int),
    ],
)


# %%
