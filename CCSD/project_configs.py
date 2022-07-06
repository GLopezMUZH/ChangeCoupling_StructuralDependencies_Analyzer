import os
import logging
from datetime import datetime
from typing import Optional, Tuple

from .utils_py import replace_timezone
from .models import (
    ProjectPaths,
    ProjectConfig,
    build_project_config,
    build_project_paths,
)


def execute_project_conf_from_file(  # pylint: disable=too-many-branches,too-many-locals,too-many-statements
    path_to_config_file: str,
) -> Tuple[ProjectConfig, ProjectPaths]:
    if not os.path.exists(path_to_config_file):
        raise FileNotFoundError(
            f'Configuration file path "{path_to_config_file}" does not exist.'
        )

    path_to_config_file = os.path.normpath(path_to_config_file)

    proj_name = None
    from_tag = None
    to_tag = None
    since_date = None
    to_date = None
    from_commit = None
    to_commit = None
    save_cache_files = None
    delete_cache_files = None
    path_to_proj_data_dir = None
    path_to_src_files = None
    proj_lang = None
    repo_url = None
    repo_type = "Git"
    only_in_branch = None

    def get_label_content(line: str, label_size: int) -> str:
        return line[label_size : len(line.rstrip())].replace("'", "")

    with open(path_to_config_file, "r", encoding="utf-8") as configfile:
        lines = configfile.readlines()
        for line in lines:
            if (line.lstrip()).startswith("proj_name:"):
                proj_name = get_label_content(line, len("proj_name:"))
            if (line.lstrip()).startswith("from_tag:"):
                from_tag = get_label_content(line, len("from_tag:"))
            if (line.lstrip()).startswith("to_tag:"):
                to_tag = get_label_content(line, len("to_tag:"))
            if (line.lstrip()).startswith("from_commit:"):
                from_commit = get_label_content(line, len("from_commit:"))
            if (line.lstrip()).startswith("to_commit:"):
                to_commit = get_label_content(line, len("to_commit:"))
            if (line.lstrip()).startswith("since_date:"):
                since_date = get_label_content(line, len("since_date:"))
            if (line.lstrip()).startswith("to_date:"):
                to_date = get_label_content(line, len("to_date:"))
            if (line.lstrip()).startswith("save_cache_files:"):
                save_cache_files = (
                    get_label_content(line, len("save_cache_files:")) != "False"
                )
            if (line.lstrip()).startswith("delete_cache_files:"):
                delete_cache_files = (
                    get_label_content(line, len("delete_cache_files:")) != "False"
                )
            if (line.lstrip()).startswith("path_to_proj_data_dir:"):
                path_to_proj_data_dir = os.path.normpath(
                    get_label_content(line, len("path_to_proj_data_dir:"))
                )
            if (line.lstrip()).startswith("path_to_src_files:"):
                path_to_src_files = get_label_content(line, len("path_to_src_files:"))
            if (line.lstrip()).startswith("proj_lang:"):
                proj_lang = get_label_content(line, len("proj_lang:"))
            if (line.lstrip()).startswith("repo_url:"):
                repo_url = get_label_content(line, len("repo_url:"))
            if (line.lstrip()).startswith("repo_type:"):
                repo_type = get_label_content(line, len("repo_type:"))
            if (line.lstrip()).startswith("only_in_branch:"):
                only_in_branch = get_label_content(line, len("only_in_branch:"))

    if proj_name is None:
        raise Exception("proj_name is required")
    if proj_lang is None:
        raise Exception("proj_lang is required")
    if repo_url is None:
        raise Exception("repo_url is required")

    proj_config = build_project_config(
        proj_name=proj_name,
        proj_lang=proj_lang,
        repo_url=repo_url,
        repo_type=repo_type,
        repo_from_tag=from_tag,
        repo_to_tag=to_tag,
        start_repo_date=_to_datetime(since_date),
        end_repo_date=_to_datetime(to_date),
        repo_from_commit=from_commit,
        repo_to_commit=to_commit,
        save_cache_files=save_cache_files,
        delete_cache_files=delete_cache_files,
        only_in_branch=only_in_branch,
    )
    proj_paths = build_project_paths(
        proj_name=proj_config["proj_name"],
        path_to_proj_data_dir=str(path_to_proj_data_dir),
        path_to_src_files=str(path_to_src_files),
    )

    log_filepath = os.path.join(proj_paths["path_to_cache_dir"], "app.log")
    print(log_filepath)

    logging.basicConfig(
        filename=log_filepath,
        level=logging.DEBUG,
        format="%(asctime)-15s [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s",
    )
    logging.debug("Started App - %s", datetime.now())

    logging.debug(proj_config)
    logging.debug(proj_paths)
    return proj_config, proj_paths


def _to_datetime(text: Optional[str]) -> Optional[datetime]:
    return datetime.strptime(text, "%d-%m-%Y") if text else None
