from .models import ProjectConfig, ProjectPaths
from .git_repository_mining_util import git_traverse


def analyse_source_repository_data(
    proj_config: ProjectConfig, proj_paths: ProjectPaths
) -> None:
    if proj_config["repo_type"] == "Git":
        git_traverse(proj_config, proj_paths)
    else:
        print(
            f"Alternative repository {proj_config['repo_type']} implementation coming soon. "
        )
    print("finished analyse_source_repository_data")
