from datetime import datetime
import os
import logging
from typing import Callable, Dict, List, Optional

from pydriller.repository import Repository
from pydriller.domain.commit import Commit, ModificationType, ModifiedFile
from git.config import GitConfigParser
from git.util import BlockingLockFile
from git.types import PathLike

from .models import FunctionCall, ProjectConfig, ProjectPaths, FileData, CommitDates
from .repository_mining_util import (
    get_file_type_validation_function,
    save_source_code,
    get_file_imports,
    save_compact_xml_parsed_code,
    jar_wrapper,
    set_hashes_to_function_calls,
)
from .utils_sql import (
    insert_git_commit,
    insert_file_commit,
    update_file_imports,
    insert_function_commit,
    update_function_to_file,
    save_raw_function_call_curr_rows,
    save_raw_function_call_deleted_rows,
)


class _LimitedBlockingLockFile(BlockingLockFile):
    MAX_BLOCK_TIME_S = 5

    def __init__(self, file_path: PathLike) -> None:
        super().__init__(file_path, max_block_time_s=self.MAX_BLOCK_TIME_S)


# set the lock behaviour to a blocking lock file with timeout
GitConfigParser.t_lock = _LimitedBlockingLockFile


def git_traverse(proj_config: ProjectConfig, proj_paths: ProjectPaths) -> None:
    repository = _git_repository_from_config(proj_config, proj_paths)
    is_valid_file_type = get_file_type_validation_function(proj_config["proj_lang"])
    for commit in repository.traverse_commits():
        process_git_commit(
            proj_config=proj_config,
            proj_paths=proj_paths,
            commit=commit,
            is_valid_file_type=is_valid_file_type,
        )


def _git_repository_from_config(
    proj_config: ProjectConfig, proj_paths: ProjectPaths
) -> Repository:
    filters: Dict[str, str | datetime] = {}
    if (
        proj_config["start_repo_date"] is not None
        and proj_config["end_repo_date"] is not None
    ):
        filters = dict(
            since=proj_config["start_repo_date"],
            to=proj_config["end_repo_date"],
        )
    elif proj_config["start_repo_date"] is not None:
        filters = dict(since=proj_config["start_repo_date"])
    elif (
        proj_config["repo_from_tag"] is not None
        and proj_config["repo_to_tag"] is not None
    ):
        filters = dict(
            from_tag=proj_config["repo_from_tag"],
            to_tag=proj_config["repo_to_tag"],
        )
    elif (
        proj_config["repo_from_commit"] is not None
        and proj_config["repo_to_commit"] is not None
    ):
        filters = dict(
            from_commit=proj_config["repo_from_commit"],
            to_commit=proj_config["repo_to_commit"],
        )

    r = Repository(
        path_to_repo=proj_paths["path_to_cache_src_dir"],
        only_modifications_with_file_types=proj_config["commit_file_types"],
        order="reverse",
        only_no_merge=True,
        only_in_branch=proj_config["only_in_branch"],
        **filters,  # type: ignore[arg-type]
    )

    print("_git_repository_from_config r")
    print(r)

    return r


def process_git_commit(
    proj_config: ProjectConfig,
    proj_paths: ProjectPaths,
    commit: Commit,
    is_valid_file_type: Callable[[str], bool],
):
    # insert git_commit
    insert_git_commit(
        proj_paths["path_to_project_db"],
        commit_hash=commit.hash,
        commit_commiter_datetime=str(commit.committer_date),
        author=commit.author.name,
        in_main_branch=True,  # commit.in_main_branch,
        merge=commit.merge,
        nr_modified_files=len(commit.modified_files),
        nr_deletions=commit.deletions,
        nr_insertions=commit.insertions,
        nr_lines=commit.lines,
    )

    for mod_file in commit.modified_files:
        if is_valid_file_type(str(mod_file._new_path)) or is_valid_file_type(
            str(mod_file._old_path)
        ):
            process_file_git_commit(proj_config, proj_paths, commit, mod_file)


def process_file_git_commit(
    proj_config: ProjectConfig,
    proj_paths: ProjectPaths,
    commit: Commit,
    mod_file: ModifiedFile,
):

    _process_file_git_commit_astdiff_parsing(proj_config, proj_paths, commit, mod_file)


def _process_file_git_commit_astdiff_parsing(
    proj_config: ProjectConfig,
    proj_paths: ProjectPaths,
    commit: Commit,
    mod_file: ModifiedFile,
) -> None:
    mod_file_data = FileData(str(mod_file._new_path))
    mod_file_data_prev = FileData(str(mod_file._old_path))

    # Create sourcediff directory
    if proj_config["save_cache_files"]:
        file_path_sourcediff = os.path.join(
            proj_paths["path_to_cache_sourcediff"], str(mod_file._new_path)
        )
        if not os.path.exists(os.path.dirname(file_path_sourcediff)):
            os.makedirs(os.path.dirname(file_path_sourcediff))

    # Save new source code
    file_path_current = None
    if (
        mod_file.change_type != ModificationType.DELETE
        and mod_file.change_type != ModificationType.RENAME
    ):
        file_path_current = os.path.join(
            proj_paths["path_to_cache_current"], str(mod_file._new_path)
        )
        save_source_code(file_path_current, mod_file.source_code)

    file_path_previous = None
    if (
        mod_file.change_type != ModificationType.ADD
        and mod_file.change_type != ModificationType.RENAME
    ):
        file_path_previous = os.path.join(
            proj_paths["path_to_cache_previous"], str(mod_file._old_path)
        )
        save_source_code(file_path_previous, mod_file.source_code_before)

    if mod_file.change_type == ModificationType.RENAME:
        print(
            "RENAME. File {0} old path: {1}, new path: {2}. TODO".format(
                mod_file.filename, mod_file._new_path, mod_file._old_path
            )
        )
        logging.info(
            "RENAME. File {0} old path: {1}, new path: {2}. TODO".format(
                mod_file.filename, mod_file._new_path, mod_file._old_path
            )
        )
        return

    # insert file_commit
    insert_file_commit(
        proj_paths["path_to_project_db"],
        mod_file_data=mod_file_data,
        commit_hash=commit.hash,
        commit_commiter_datetime=commit.committer_date,
        commit_file_name=mod_file.filename,
        commit_new_path=mod_file.new_path,
        commit_old_path=mod_file.old_path,
        change_type=mod_file.change_type,
    )

    # update file imports
    fis = get_file_imports(
        proj_lang=proj_config["proj_lang"],
        path_to_src_files=proj_paths["path_to_src_files"],
        source_code=mod_file.source_code,
        mod_file_data=mod_file_data,
    )
    fis_prev = get_file_imports(
        proj_lang=proj_config["proj_lang"],
        path_to_src_files=proj_paths["path_to_src_files"],
        source_code=mod_file.source_code_before,
        mod_file_data=mod_file_data_prev,
    )

    update_file_imports(
        mod_file_data,
        fis,
        fis_prev,
        proj_paths["path_to_project_db"],
        commit_hash=commit.hash,
        commit_datetime=str(commit.committer_date),
    )

    # function_commit
    insert_function_commit(proj_paths["path_to_project_db"], mod_file, commit)

    # update function_to_file
    update_function_to_file(proj_paths["path_to_project_db"], mod_file, commit)

    # update function_call
    update_function_calls(
        proj_config, proj_paths, mod_file, commit, file_path_current, file_path_previous
    )


# TODO list to array, maybe
# TODO handle mod_file._old_path != mod_file._new_path
def update_function_calls(
    proj_config: ProjectConfig,
    proj_paths: ProjectPaths,
    mod_file: ModifiedFile,
    commit: Commit,
    file_path_current: str,
    file_path_previous: Optional[str] = None,
):

    mod_file_data = FileData(str(mod_file._new_path))

    if proj_config["proj_lang"] == "java" or proj_config["proj_lang"] == "cpp":
        # Current source code
        curr_function_calls: List[FunctionCall] = []
        if file_path_current is not None:
            logging.debug(file_path_current)
            if not os.path.exists(file_path_current):
                logging.warning(
                    "file_path_current does not exist {0}".format(file_path_current)
                )
            # get compact xml parsed source
            curr_src_args = [
                proj_config["path_to_src_compact_xml_parsing"],
                file_path_current,
            ]
            result = jar_wrapper(*curr_src_args)
            # convert to string -> xml
            curr_src_str = b"".join(result).decode("utf-8")

            save_compact_xml_parsed_code(
                path_to_cache_dir=proj_paths["path_to_cache_current"],
                relative_file_path=str(mod_file._new_path),
                source_text=curr_src_str,
            )

            """
            calling_function_unqualified_name,
            calling_function_nr_parameters,
            called_function_unqualified_name       
            """
            if proj_config["proj_lang"] == "java":
                # curr_src_xml = BeautifulSoup(curr_src_str, "xml")
                # curr_function_calls = get_function_calls_java(curr_src_xml)
                print("WOULD BE get_function_calls_java")
            else:
                curr_function_calls = []
                logging.info("TODO")
                print("TODO")

        # Previous source code
        prev_function_calls: List[FunctionCall] = []
        if (
            mod_file.change_type != ModificationType.ADD
            and file_path_previous is not None
        ):
            logging.debug(file_path_previous)
            if not os.path.exists(file_path_previous):
                logging.warning(
                    "file_path_previous does not exist {0}".format(file_path_previous)
                )
            # get compact xml parsed source
            prev_src_args = [
                proj_config["path_to_src_compact_xml_parsing"],
                file_path_previous,
            ]
            result = jar_wrapper(*prev_src_args)
            # convert to string -> xml
            prev_src_str = b"".join(result).decode("utf-8")

            save_compact_xml_parsed_code(
                path_to_cache_dir=proj_paths["path_to_cache_previous"],
                relative_file_path=str(mod_file._new_path),
                source_text=prev_src_str,
            )

            if proj_config["proj_lang"] == "java":
                # prev_src_xml = BeautifulSoup(prev_src_str, "xml")
                # prev_function_calls = get_function_calls_java(prev_src_xml)
                print("WOULD BE get_function_calls_java")
            else:
                curr_function_calls = []
                print("TODO")
                logging.info("TODO")

        cm_dates = CommitDates(commit.hash, commit.committer_date)
        rows_curr, rows_deleted = set_hashes_to_function_calls(
            curr_function_calls, prev_function_calls, cm_dates
        )
        logging.debug("Deleted: ")
        logging.debug(rows_deleted)
        # arr_all_function_calls = complete_function_calls_data(arr_all_function_calls)

        """
        FUNCTION_CALL
        file_name
        file_dir_path
        file_path
        calling_function_unqualified_name
        calling_function_nr_parameters
        called_function_unqualified_name
        called_function_nr_parameters
        commit_hash_start
        commit_start_datetime
        commit_hash_oldest
        commit_oldest_datetime
        commit_hash_end
        commit_end_datetime
        closed
        """
        save_raw_function_call_curr_rows(
            proj_paths["path_to_project_db"], rows_curr, mod_file_data
        )
        save_raw_function_call_deleted_rows(
            proj_paths["path_to_project_db"], rows_deleted, mod_file_data
        )

        # save_call_commit_rows() # MIGHT NOT NEED THEM

    else:
        print("No current parser for the project language.")
