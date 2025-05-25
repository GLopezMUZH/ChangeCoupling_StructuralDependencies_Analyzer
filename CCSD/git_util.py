import logging
import os

from git.cmd import Git
from git.repo import Repo
from git.exc import GitCommandError


def checkout_repo(
    repo_url: str, path_to_cache_src_dir: str, branch_or_commit: str
) -> None:
    print("start checkout_repo")

    set_safe_directory(path_to_cache_src_dir)

    if not os.path.exists(os.path.dirname(path_to_cache_src_dir)):
        os.makedirs(os.path.dirname(path_to_cache_src_dir))

    if not os.path.exists(os.path.join(path_to_cache_src_dir, ".git")):
        logging.info("Start git clone")
        Repo.clone_from(repo_url, path_to_cache_src_dir)
        logging.info("End git clone")

    logging.info("Reset cached source to current state")
    g = Git(path_to_cache_src_dir)
    g.checkout(branch_or_commit)
    print("finished checkout_repo")


def set_safe_directory(directory):
    # Initialize a Git object
    git_cmd = Git()

    dir = '/var/project/' + directory

    # Execute the Git command to add the safe directory
    try:
        git_cmd.config("--global", "--add", "safe.directory", dir)
        print(f"Added {dir} as a safe directory.")
    except GitCommandError as e:
        print(f"Failed to add {dir} as a safe directory: {e}")

