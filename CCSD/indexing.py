import os
from itertools import islice
import sqlite3
from typing import NamedTuple

from .models import ProjectPaths


def execute_intitial_indexing(proj_paths: ProjectPaths, proj_lang: str) -> None:
    if proj_lang == "java":
        create_file_pkg_table(proj_paths=proj_paths)
    print("finished execute_intitial_indexing")


_FileInfo = NamedTuple(
    "_FileInfo",
    [
        ("file_name", str),
        ("file_dir_path", str),
        ("file_path", str),
        ("file_pkg", str),
        ("class_pkg", str),
    ],
)


def create_file_pkg_table(proj_paths: ProjectPaths) -> None:
    f_list = []
    local_src_dir = os.path.normpath(proj_paths["path_to_cache_src_dir"])
    for dirs, _subdirs, files in os.walk(local_src_dir):
        for f in files:
            if ".java" in f:
                f_full_path = os.path.join(dirs, f)
                f_path = os.path.relpath(f_full_path, local_src_dir)
                f_dir_path = os.path.dirname(f_path)

                with open(f_full_path, "r", encoding="utf-8") as codefile:
                    not_found = True
                    while not_found:
                        try:
                            lines = list(islice(codefile, 100))
                            for code_line in lines:
                                if (code_line.lstrip()).startswith("package "):
                                    f_pkg = code_line[
                                        8 : len(code_line.rstrip())
                                    ].replace(";", "")
                                    f_list.append(
                                        _FileInfo(
                                            file_name=f,
                                            file_dir_path=f_dir_path,
                                            file_path=f_path,
                                            file_pkg=f_pkg,
                                            class_pkg=f"{f_pkg}.{f.replace('.java', '')}",
                                        )
                                    )
                                    not_found = False
                            if not lines:
                                break
                        except UnicodeEncodeError:
                            not_found = False

    with sqlite3.connect(proj_paths["path_to_project_db"]) as conn:
        cur = conn.cursor()

        cur.execute("""DROP TABLE IF EXISTS file_pkg""")
        cur.execute(
            """CREATE TABLE "file_pkg" ("file_name" TEXT, "file_dir_path" TEXT, "file_path" TEXT, "file_pkg" TEXT, "class_pkg" TEXT);"""
        )

        cur.executemany('INSERT INTO "file_pkg" VALUES (?, ?, ?, ?, ?)', f_list)
        conn.commit()
