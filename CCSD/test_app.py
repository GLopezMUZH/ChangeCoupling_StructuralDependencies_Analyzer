# %%
import os
import logging
from datetime import datetime

from changeAnalyzerSD.models import ProjectPaths

from .repository_mining import analyse_source_repository_data
from .utils_sql import create_db_tables
from .project_configs import execute_project_conf_from_file
from .git_util import checkout_repo


# %%
def main() -> None:
    path_to_config_file = os.path.normpath('..\\project_config\\PX4-Autopilot.pconfig')  # glucosio_small

    os.path.exists(path_to_config_file)
    proj_config, proj_paths = execute_project_conf_from_file(
        str(path_to_config_file))

    # can only log after seting log file path
    logging.info('Started App ---------- %s', datetime.now())

    init_db(proj_paths)

    checkout_repo(proj_config['repo_url'], proj_paths['path_to_cache_src_dir'], proj_config['only_in_branch'])
    # execute_intitial_indexing(proj_paths)

    analyse_source_repository_data(proj_config=proj_config, proj_paths=proj_paths)

    logging.info('Finished App ---------- %s', datetime.now())
    print(f'Finished App -------------{datetime.now()}')


def init_db(proj_paths: ProjectPaths) -> None:
    # logging.info('Initialize the db.')
    create_db_tables(proj_paths, drop=True)


# %%
if __name__ == '__main__':
    main()

# %%
