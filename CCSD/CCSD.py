# %%
import logging
from datetime import datetime
import sys

from CCSD.models import ProjectPaths

from .project_configs import execute_project_conf_from_file
from .git_util import checkout_repo
from .indexing import execute_intitial_indexing
from .repository_mining import analyse_source_repository_data
from .utils_sql import create_db_tables


# error messages
INVALID_PATH_MSG = "Error: Invalid file path/name. Path %s does not exist."


def main() -> None:
    """
    since_date format '12-11-2019'
    """
    print(f"Started App ------------ {datetime.now()}")

    args = sys.argv[1:]

    # argument format -P proj_name -from_tag tag -to_tag tag
    if "-C" in args:
        f_idx = args.index("-C")
        path_to_config_file = args[f_idx + 1]
        proj_config, proj_paths = execute_project_conf_from_file(path_to_config_file)
    else:
        raise Exception("Configuration file is mandatory: -C path")

    # can only log after seting log file path
    print(("Started App ---------- %s", datetime.now()))
    logging.info("Started App ---------- ", datetime.now())

    print("proj_paths")
    print(proj_paths)

    if "--no-init-db" in args:
        logging.info("Not re-initialized database...")
    else:
        init_db(proj_paths)

    # if '-init_index_yes' in args:
    checkout_repo(
        proj_config["repo_url"],
        proj_paths["path_to_cache_src_dir"],
        proj_config["only_in_branch"],
    )
    execute_intitial_indexing(proj_paths, proj_config["proj_lang"])

    analyse_source_repository_data(proj_config=proj_config, proj_paths=proj_paths)

    logging.info("Finished App ---------- %s", datetime.now())
    print(f"Finished App ------------- {datetime.now()}")


def init_db(proj_paths: ProjectPaths) -> None:
    logging.info("Initialize the db.")
    print("Initialize the db.")
    create_db_tables(proj_paths, drop=True)


# %%
if __name__ == "__main__":
    main()
