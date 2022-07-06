import logging
import os
import sqlite3
from datetime import datetime
from typing import Optional, List

from pydriller.domain.commit import Commit, ModifiedFile, ModificationType

from .models import (
    ExtendedFunctionCall,
    FileImport,
    CallCommitInfo,
    ActionClass,
    FileData,
    ProjectPaths,
)


def create_db_tables(proj_paths: ProjectPaths, drop: bool = False) -> None:
    print(
        "exist path_to_proj_data_dir %s ",
        str(proj_paths["path_to_proj_data_dir"]),
        os.path.exists(str(proj_paths["path_to_proj_data_dir"])),
    )
    print(os.path.abspath(proj_paths["path_to_proj_data_dir"]))
    absolute_path = os.path.abspath(__file__)
    print("Full path: " + absolute_path)
    print("Directory Path: " + os.path.dirname(absolute_path))

    if not os.path.exists(str(proj_paths["path_to_proj_data_dir"])):
        os.makedirs(str(proj_paths["path_to_proj_data_dir"]))
    print("create_db_tables drop", drop)
    create_commit_based_tables(proj_paths["path_to_project_db"], drop)


def create_commit_based_tables(path_to_project_db: str, drop: bool = False) -> None:
    print("create_commit_based_tables drop", drop)
    con = sqlite3.connect(path_to_project_db)
    cur = con.cursor()

    if drop:
        try:
            cur.execute("""DROP TABLE git_commit""")
        except sqlite3.Error as error:
            logging.debug("git_commit %s", error)
        try:
            cur.execute("""DROP TABLE file_commit""")
        except sqlite3.Error as error:
            logging.debug("file_commit %s", error)
        try:
            cur.execute("""DROP TABLE function_commit""")
        except sqlite3.Error as error:
            logging.debug("function_commit %s", error)
        try:
            cur.execute("""DROP TABLE file_import""")
        except sqlite3.Error as error:
            logging.debug("file_import %s", error)
        try:
            cur.execute("""DROP TABLE call_commit""")
        except sqlite3.Error as error:
            logging.debug("call_commit %s", error)
        try:
            cur.execute("""DROP TABLE function_to_file""")
        except sqlite3.Error as error:
            logging.debug("function_to_file %s", error)
        try:
            cur.execute("""DROP TABLE function_call""")
        except sqlite3.Error as error:
            logging.debug("function_call %s", error)
        try:
            cur.execute("""DROP TABLE raw_function_call""")
        except sqlite3.Error as error:
            logging.debug("raw_function_call %s", error)

    cur.execute(
        """CREATE TABLE IF NOT EXISTS git_commit
                (commit_hash text, commit_commiter_datetime text, author text,
                in_main_branch integer, merge integer,
                nr_modified_files integer, nr_deletions integer, nr_insertions integer, nr_lines integer,
                primary key (commit_hash))"""
    )
    print("create_commit_based_tables created git_commit")

    cur.execute(
        """CREATE TABLE IF NOT EXISTS file_commit
                (file_name text, file_dir_path text, file_path text,
                commit_hash text,
                commit_commiter_datetime text, commit_file_name text,
                commit_new_path text, commit_old_path text, change_type text,
                path_change integer,
                primary key (file_path, commit_hash))"""
    )

    cur.execute(
        """CREATE TABLE IF NOT EXISTS function_commit
                (file_name text, file_dir_path text, file_path text,
                function_unqualified_name text, function_name text, function_long_name text,
                function_parameters text, function_nloc integer,
                commit_hash text, commit_commiter_datetime text,
                commit_file_name text, commit_new_path text, commit_old_path text,
                path_change integer, commit_type,
                primary key (file_path, function_long_name, commit_hash))"""
    )

    cur.execute(
        """CREATE TABLE IF NOT EXISTS file_import
                (file_name text, file_dir_path text, file_path text,
                import_file_path text, import_file_name text, import_file_dir_path text,
                import_file_pkg text,
                commit_hash_start text, commit_start_datetime text,
                commit_hash_oldest text, commit_oldest_datetime text,
                commit_hash_end text, commit_end_datetime text, closed integer,
                primary key (file_path, import_file_path, commit_hash_start, commit_hash_oldest, commit_hash_end))"""
    )

    # cur.execute('''CREATE TABLE IF NOT EXISTS call_commit
    #             (file_name text, file_dir_path text, file_path text,
    #             calling_function_unqualified_name text, calling_function_name text,
    #             calling_function_long_name text, calling_function_parameters text,
    #             called_function_unqualified_name text, called_function_name text,
    #             called_function_long_name text, called_function_parameters text,
    #             commit_hash text, commit_commiter_datetime text,
    #             primary key (file_path, calling_function_long_name, called_function_long_name, commit_hash))''')

    cur.execute(
        """CREATE TABLE IF NOT EXISTS function_to_file
                (file_name text, file_dir_path text, file_path text,
                function_unqualified_name text, function_name text,
                function_long_name text, function_parameters text,
                commit_hash_start text, commit_start_datetime text,
                commit_hash_oldest text, commit_oldest_datetime text,
                commit_hash_end text, commit_end_datetime text, closed integer,
                primary key (file_path, function_long_name, commit_hash_start, commit_hash_oldest, commit_hash_end))"""
    )

    cur.execute(
        """CREATE TABLE IF NOT EXISTS function_call
                (file_name text, file_dir_path text, file_path text,
                calling_function_unqualified_name text, calling_function_name text,
                calling_function_long_name text, calling_function_parameters text,
                called_function_unqualified_name text, called_function_name text,
                called_function_long_name text, called_function_parameters text,
                commit_hash_start text, commit_start_datetime text,
                commit_hash_oldest text, commit_oldest_datetime text,
                commit_hash_end text, commit_end_datetime text, closed integer,
                primary key (
                    file_path, calling_function_long_name, called_function_long_name, commit_hash_start, commit_hash_oldest, commit_hash_end
                ))"""
    )

    cur.execute(
        """CREATE TABLE IF NOT EXISTS raw_function_call
                (file_name text, file_dir_path text, file_path text,
                calling_function_unqualified_name text, calling_function_nr_parameters integer,
                called_function_unqualified_name text, called_function_nr_parameters integer,
                commit_hash_start text, commit_start_datetime text,
                commit_hash_oldest text, commit_oldest_datetime text,
                commit_hash_end text, commit_end_datetime text, closed integer,
                primary key (file_path, calling_function_unqualified_name, calling_function_nr_parameters,
                called_function_unqualified_name, commit_hash_start, commit_hash_oldest, commit_hash_end))"""
    )

    con.commit()
    cur.close()
    print("finished create_commit_based_tables")


def insert_git_commit(
    path_to_project_db: str,
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
    try:
        con_analytics_db = sqlite3.connect(path_to_project_db)
        cur = con_analytics_db.cursor()

        sql_string = f"""INSERT INTO git_commit
                    (commit_hash, commit_commiter_datetime, author,
                    in_main_branch, merge,
                    nr_modified_files, nr_deletions, nr_insertions, nr_lines)
                VALUES (
                    '{commit_hash}','{commit_commiter_datetime}','{author}','{in_main_branch}','{merge}','{nr_modified_files}','{nr_deletions}',
                    '{nr_insertions}','{nr_lines}'
                );"""

        cur.execute(sql_string)
        con_analytics_db.commit()
        cur.close()
    except sqlite3.Error as err:
        con_analytics_db.rollback()
        cur.close()
        print(f"IntegrityError. UNIQUE failed for [{commit_hash}] ")
        logging.error("[%s] ", commit_hash)
        logging.error(
            "An exception of type %s occurred. Arguments:\n%s",
            type(err).__name__,
            repr(err.args),
        )


def insert_file_commit(
    path_to_project_db: str,
    mod_file_data: FileData,
    commit_hash: str,
    commit_commiter_datetime: datetime,
    commit_file_name: str,
    commit_new_path: Optional[str],
    commit_old_path: Optional[str],
    change_type: ModificationType,
) -> None:
    try:
        con_analytics_db = sqlite3.connect(path_to_project_db)
        cur = con_analytics_db.cursor()

        path_change = 0 if commit_new_path == commit_old_path else 1

        sql_string = f"""INSERT INTO file_commit
                    (file_name, file_dir_path, file_path,
                    commit_hash, commit_commiter_datetime, commit_file_name,
                    commit_new_path, commit_old_path, change_type, path_change)
                VALUES (
                    '{mod_file_data.get_file_name()}','{mod_file_data.get_file_dir_path()}','{mod_file_data.get_file_path()}','{commit_hash}',
                    '{commit_commiter_datetime}','{commit_file_name}','{commit_new_path}','{commit_old_path}','{change_type}','{path_change}'
                );"""

        cur.execute(sql_string)
        con_analytics_db.commit()
        cur.close()
    except sqlite3.Error as err:
        con_analytics_db.rollback()
        cur.close()
        print(
            f"IntegrityError. UNIQUE failed for [{commit_hash},{mod_file_data.get_file_path()}] "
        )
        logging.error("[%s,%s] ", commit_hash, mod_file_data.get_file_path())
        logging.error(
            "An exception of type %s occurred. Arguments:\n%s",
            type(err).__name__,
            repr(err.args),
        )


def get_previous_file_import_long_names(
    path_to_project_db: str, mod_file_data: FileData
) -> Optional[List[str]]:
    try:

        con_analytics_db = sqlite3.connect(path_to_project_db)
        cur = con_analytics_db.cursor()

        sql_string = f"""SELECT import_file_path
        FROM file_import
        WHERE file_path = '{mod_file_data.get_file_path()}'
        AND closed = 0"""

        cur.execute(sql_string)
        result = cur.fetchall()

        con_analytics_db.commit()
        cur.close()
        return result

    except sqlite3.Error as err:
        con_analytics_db.rollback()
        cur.close()
        logging.error(
            "An exception of type %s occurred. Arguments:\n%s",
            type(err).__name__,
            repr(err.args),
        )
        return None


def update_file_imports(
    mod_file_data: FileData,
    fis: List[FileImport],
    fis_prev: List[FileImport],
    path_to_project_db: str,
    commit_hash: str,
    commit_datetime: str,
) -> None:

    if len(fis) == 0:
        logging.warning("fis is empty.")
        return

    try:
        con_analytics_db = sqlite3.connect(path_to_project_db)
        cur = con_analytics_db.cursor()

        # TODO change to parsing previous file....
        previous_file_import_long_names_from_db = get_previous_file_import_long_names(
            path_to_project_db, mod_file_data
        )
        curr_file_imports_long_names = [f.get_import_file_path() for f in fis]
        previous_file_import_long_names = [f.get_import_file_path() for f in fis_prev]

        # TODO make absolute empty table
        # first commit on db
        if (
            previous_file_import_long_names_from_db is None
            or len(previous_file_import_long_names_from_db) == 0
        ):
            logging.debug("First commit. Add %d", len(fis))
            for fi in fis:
                sql_string = f"""INSERT INTO file_import
                            (file_name, file_dir_path, file_path,
                            import_file_name, import_file_path,
                            import_file_dir_path, import_file_pkg,
                            commit_hash_oldest, commit_oldest_datetime, closed)
                        VALUES (
                            '{fi.get_file_name()}','{fi.get_file_dir_path()}','{fi.get_file_path()}','{fi.get_import_file_name()}',
                            '{fi.get_import_file_path()}','{fi.get_import_file_dir_path()}','{fi.get_import_file_pkg()}',
                            '{commit_hash}','{commit_datetime}',0
                        );"""
                # logging.debug(sql_string)
                cur.execute(sql_string)
            con_analytics_db.commit()
        else:

            # from the commit we have the prev_fis from the previous source code
            # get existing in prev but not in curr
            added_file_imports = list(
                set(curr_file_imports_long_names) - set(previous_file_import_long_names)
            )
            # get existing in prev but not in curr
            deleted_file_imports = list(
                set(previous_file_import_long_names) - set(curr_file_imports_long_names)
            )
            # get intersection
            unchanged_file_imports = list(
                set(curr_file_imports_long_names).intersection(
                    previous_file_import_long_names
                )
            )

            logging.debug("added_file_imports len %d", len(added_file_imports))
            logging.debug("deleted_file_imports len %d", len(deleted_file_imports))
            logging.debug("unchanged_file_imports len %d", len(unchanged_file_imports))

            # handle added file_imports
            for fi in [
                fi for fi in fis if fi.get_import_file_path() in added_file_imports
            ]:
                sql_string = f"""INSERT INTO file_import
                            (file_name, file_dir_path, file_path,
                            import_file_name, import_file_path,
                            import_file_dir_path, import_file_pkg,
                            commit_hash_start, commit_start_datetime,
                            commit_hash_oldest, commit_oldest_datetime, closed)
                        VALUES (
                            '{fi.get_file_name()}','{fi.get_file_dir_path()}','{fi.get_file_path()}','{fi.get_import_file_name()}',
                            '{fi.get_import_file_path()}','{fi.get_import_file_dir_path()}','{fi.get_import_file_pkg()}',
                            '{commit_hash}','{commit_datetime}','{commit_hash}','{commit_datetime}',0
                        )
                        ON CONFLICT (file_path, import_file_path, commit_hash_start, commit_hash_oldest, commit_hash_end)
                        DO UPDATE SET commit_hash_start = excluded.commit_hash_start,
                            commit_start_datetime = excluded.commit_start_datetime,
                            commit_hash_oldest=excluded.commit_hash_oldest,
                            commit_oldest_datetime=excluded.commit_oldest_datetime;"""
                logging.debug(sql_string)
                cur.execute(sql_string)

            # handle deleted file_imports
            for file_import in deleted_file_imports:
                sql_string = f"""UPDATE file_import SET
                            commit_hash_end='{commit_hash}', commit_end_datetime='{commit_datetime}',
                            closed=1
                            WHERE
                            file_path='{mod_file_data.get_file_path()}'
                            AND import_file_path='{file_import[0]}'
                            closed = 0;"""
                logging.debug(sql_string)
                cur.execute(sql_string)

            # handle unchanged file_imports
            for fi in [
                f for f in fis if f.get_import_file_path() in unchanged_file_imports
            ]:
                sql_string = f"""UPDATE file_import SET
                            commit_hash_oldest='{commit_hash}', commit_oldest_datetime='{commit_datetime}'
                            WHERE
                            file_path='{mod_file_data.get_file_path()}'
                            AND import_file_path='{fi.get_import_file_path()}'
                            AND closed=0;"""
                logging.debug(sql_string)
                cur.execute(sql_string)

            con_analytics_db.commit()

        cur.close()
    except sqlite3.Error as err:
        con_analytics_db.rollback()
        cur.close()
        logging.error(
            "An exception of type %s occurred. Arguments:\n%s",
            type(err).__name__,
            repr(err.args),
        )


def insert_function_commit(
    path_to_project_db: str, mod_file: ModifiedFile, commit: Commit
) -> None:
    mod_file_data = FileData(str(mod_file.new_path))
    try:
        con_analytics_db = sqlite3.connect(path_to_project_db)
        cur = con_analytics_db.cursor()

        commit_previous_functions = [f.long_name for f in mod_file.methods_before]
        commit_current_functions = [f.long_name for f in mod_file.methods]

        # get added functions (existing in curr but not prev)
        added_functions = list(
            set(commit_current_functions) - set(commit_previous_functions)
        )
        # get deleted functions (existing in prev but not in curr)
        deleted_functions = list(
            set(commit_previous_functions) - set(commit_current_functions)
        )

        # added, deleted and modified methods appear in changed methods
        for cm in mod_file.changed_methods:
            if cm.long_name in added_functions:
                action_class = ActionClass.ADD
            elif cm.long_name in deleted_functions:
                action_class = ActionClass.DELETE
            else:
                action_class = ActionClass.MODIFIY
            params = ",".join(cm.parameters)
            f_unqualified_name = (cm.name).split("::")[len((cm.name).split("::")) - 1]
            path_change = 0 if mod_file.new_path == mod_file.old_path else 1

            sql_string = f"""INSERT INTO function_commit
                        (file_name, file_dir_path, file_path,
                        function_unqualified_name, function_name, function_long_name, function_parameters, function_nloc,
                        commit_hash, commit_commiter_datetime,
                        commit_file_name, commit_new_path, commit_old_path,
                        path_change, commit_type)
                    VALUES (
                        '{mod_file_data.get_file_name()}','{mod_file_data.get_file_dir_path()}','{mod_file_data.get_file_path()}',
                        '{f_unqualified_name}','{cm.name}','{cm.long_name}','{params}','{cm.nloc}','{commit.hash}','{commit.committer_date}',
                        '{mod_file.filename}','{mod_file.new_path}','{mod_file.old_path}','{path_change}','{action_class}'
                    );"""

            cur.execute(sql_string)

        con_analytics_db.commit()
        cur.close()
    except sqlite3.Error as err:
        con_analytics_db.rollback()
        cur.close()
        logging.error(
            "An exception of type %s occurred. Arguments:\n%s",
            type(err).__name__,
            repr(err.args),
        )


def get_previous_active_functions_in_file(
    path_to_project_db: str, mod_file: ModifiedFile
) -> Optional[List[str]]:
    mod_file_data = FileData(str(mod_file.new_path))
    try:

        con_analytics_db = sqlite3.connect(path_to_project_db)
        cur = con_analytics_db.cursor()

        sql_string = f"""SELECT function_long_name
        FROM function_to_file
        WHERE file_path = '{mod_file_data.get_file_path()}'
        AND closed = 0"""

        cur.execute(sql_string)
        result = cur.fetchall()

        con_analytics_db.commit()
        cur.close()
        return result

    except sqlite3.Error as err:
        con_analytics_db.rollback()
        cur.close()
        logging.error(
            "An exception of type %s occurred. Arguments:\n%s",
            type(err).__name__,
            repr(err.args),
        )
        return None


def update_function_to_file(
    path_to_project_db: str, mod_file: ModifiedFile, commit: Commit
) -> None:
    mod_file_data = FileData(str(mod_file.new_path))
    try:
        con_analytics_db = sqlite3.connect(path_to_project_db)
        cur = con_analytics_db.cursor()

        commit_previous_functions = [f.long_name for f in mod_file.methods_before]
        commit_current_functions = [f.long_name for f in mod_file.methods]
        commit_changed_functions = [f.long_name for f in mod_file.changed_methods]

        # get added functions (existing in curr but not prev)
        added_functions = list(
            set(commit_current_functions) - set(commit_previous_functions)
        )
        # get deleted functions (existing in prev but not in curr)
        deleted_functions = list(
            set(commit_previous_functions) - set(commit_current_functions)
        )
        # get just changed functions
        changed_functions = list(
            set(commit_changed_functions)
            - set(added_functions)
            - set(deleted_functions)
        )
        # get not changed functions
        unchanged_functions = list(
            set(commit_previous_functions).intersection(commit_current_functions)
            - set(changed_functions)
        )

        logging.debug("added_functions len %d", len(added_functions))
        logging.debug("deleted_functions len %d", len(deleted_functions))
        logging.debug("changed_functions len %d", len(changed_functions))
        logging.debug("unchanged_functions len %d", len(unchanged_functions))

        # mod_file.methods include added, changed and unchanged
        # on method added, the commit_hash_start will be set to the current
        # on methods previously exisitng, the commit_hash_start will be updated to the current because we work the repository in reverse order
        for cm in mod_file.methods:
            params = ",".join(cm.parameters)

            f_unqualified_name = (cm.name).split("::")[len((cm.name).split("::")) - 1]

            # Added functions
            if cm.long_name in added_functions:
                # logging.debug("Added funciton {0}".format(cm.long_name))
                sql_string = f"""INSERT INTO function_to_file
                            (file_name, file_dir_path, file_path,
                            function_unqualified_name, function_name,
                            function_long_name, function_parameters,
                            commit_hash_start, commit_start_datetime,
                            commit_hash_oldest, commit_oldest_datetime,
                            closed)
                        VALUES (
                            '{mod_file_data.get_file_name()}','{mod_file_data.get_file_dir_path()}','{mod_file_data.get_file_path()}',
                            '{f_unqualified_name}','{cm.name}','{cm.long_name}','{params}','{commit.hash}','{commit.committer_date}',
                            '{commit.hash}','{commit.committer_date}',0
                        )
                        ON CONFLICT (file_path, function_long_name, commit_hash_start, commit_hash_oldest, commit_hash_end)
                        DO UPDATE SET commit_hash_start = excluded.commit_hash_start,
                            commit_start_datetime = excluded.commit_start_datetime,
                            commit_hash_oldest=excluded.commit_hash_oldest,
                            commit_oldest_datetime=excluded.commit_oldest_datetime;"""
                cur.execute(sql_string)

            # Changed and unchanged functions
            if cm.long_name in changed_functions or cm.long_name in unchanged_functions:
                # logging.debug("Changed or unchanged funciton {0}".format(cm.long_name))
                sql_string = f"""UPDATE function_to_file SET
                                commit_hash_oldest='{commit.hash}', commit_oldest_datetime='{commit.committer_date}',
                                closed = 1
                                WHERE
                                file_path='{mod_file_data.get_file_path()}'
                                AND function_long_name='{cm.long_name}' AND closed = 0;"""

                cur.execute(sql_string)
                # logging.debug("cur.rowcount {0}".format(cur.rowcount))

                if cur.rowcount <= 0:
                    # logging.debug("Changed or unchanged funciton {0} didnt exist in db, make insert. ".format(cm.long_name))
                    sql_string = f"""INSERT INTO function_to_file
                                (file_name, file_dir_path, file_path,
                                function_unqualified_name, function_name,
                                function_long_name, function_parameters,
                                commit_hash_oldest, commit_oldest_datetime, closed)
                            VALUES (
                                '{mod_file_data.get_file_name()}','{mod_file_data.get_file_dir_path()}','{mod_file_data.get_file_path()}',
                                '{f_unqualified_name}','{cm.name}','{cm.long_name}','{params}','{commit.hash}','{commit.committer_date}',0
                            )
                            ON CONFLICT (file_path, function_long_name, commit_hash_start, commit_hash_oldest, commit_hash_end)
                            DO UPDATE SET commit_hash_oldest = excluded.commit_hash_oldest,
                                commit_oldest_datetime = excluded.commit_oldest_datetime;"""
                    cur.execute(sql_string)

        # Deleted functions
        for cm in mod_file.changed_methods:
            if cm.long_name in deleted_functions:
                logging.debug("Deleted function_to_file: %s", cm.long_name)
                params = ",".join(cm.parameters)

                f_unqualified_name = (cm.name).split("::")[
                    len((cm.name).split("::")) - 1
                ]

                # previous_active_functions_in_file:
                if cm.long_name in commit_previous_functions:
                    # TODO check if 2 times processing
                    sql_string = f"""UPDATE function_to_file SET
                                commit_hash_end='{commit.hash}', commit_end_datetime='{commit.committer_date}',
                                commit_hash_oldest='{commit.hash}', commit_oldest_datetime='{commit.committer_date}',
                                closed = 1
                                WHERE
                                file_path='{mod_file_data.get_file_path()}'
                                AND function_long_name='{cm.long_name}' AND closed = 0;"""
                else:
                    # because we work from tag to tag it might be that the entry does not exist
                    logging.debug(
                        "Deleted funciton %s didnt exist in db, make insert. ",
                        cm.long_name,
                    )
                    sql_string = f"""INSERT INTO function_to_file
                                (file_name, file_dir_path, file_path,
                                function_unqualified_name, function_name,
                                function_long_name, function_parameters,
                                commit_hash_oldest, commit_oldest_datetime,
                                commit_hash_end, commit_end_datetime, closed)
                            VALUES (
                                '{mod_file_data.get_file_name()}','{mod_file_data.get_file_dir_path()}','{mod_file_data.get_file_path()}',
                                '{f_unqualified_name}','{cm.name}','{cm.long_name}',{params},'{commit.hash}','{commit.committer_date}',
                                '{commit.hash}','{commit.committer_date}',1
                            )
                            ON CONFLICT (file_path, function_long_name, commit_hash_start, commit_hash_oldest, commit_hash_end)
                            DO UPDATE SET commit_hash_end = excluded.commit_hash_end,
                                commit_end_datetime = excluded.commit_end_datetime,
                                commit_hash_oldest=excluded.commit_hash_oldest,
                                commit_oldest_datetime=excluded.commit_oldest_datetime,
                                closed = excluded.closed;"""
                cur.execute(sql_string)

        con_analytics_db.commit()
        cur.close()
    except sqlite3.Error as err:
        con_analytics_db.rollback()
        cur.close()
        logging.error(
            "An exception of type %s occurred. Arguments:\n%s",
            type(err).__name__,
            repr(err.args),
        )


def insert_or_update_call_commit_deprecated(
    con_analytics_db: sqlite3.Connection,
    cur: sqlite3.Cursor,
    call_commit: CallCommitInfo,
    commit_hash_start: str,
    commit_start_datetime: str,
    commit_hash_end: Optional[str] = "",
    commit_end_datetime: Optional[str] = "",
) -> None:
    execute_sql = False

    if call_commit.get_action_class() is ActionClass.DELETE:
        commit_hash_end = commit_hash_start
        commit_end_datetime = commit_start_datetime
        sql_string = f"""INSERT INTO call_commit
                    (file_name, file_dir_path, file_path,
                    calling_function, called_function, commit_hash_end, commit_end_datetime)
                VALUES (
                    '{call_commit.get_file_name()}','{call_commit.get_file_dir_path()}','{call_commit.get_file_path()}',
                    '{call_commit.get_calling_function()}','{call_commit.get_called_function()}','{commit_hash_end}','{commit_end_datetime}'
                )
                ON CONFLICT (file_path, calling_function, called_function)
                DO UPDATE SET commit_hash_end = excluded.commit_hash_end,
                    commit_end_datetime = excluded.commit_end_datetime;"""
        execute_sql = True
    elif (
        call_commit.get_action_class() is ActionClass.INSERT
        or call_commit.get_action_class() is ActionClass.ADD
    ):
        sql_string = f"""INSERT INTO call_commit
                    (file_name, file_dir_path, file_path,
                    calling_function, called_function,
                    commit_hash_start, commit_start_datetime)
                VALUES (
                    '{call_commit.get_file_name()}','{call_commit.get_file_dir_path()}','{call_commit.get_file_path()}',
                    '{call_commit.get_calling_function()}','{call_commit.get_called_function()}','{commit_hash_start}','{commit_start_datetime}'
                )
                ON CONFLICT (file_path, calling_function, called_function)
                DO UPDATE SET commit_hash_start = excluded.commit_hash_start,
                    commit_start_datetime = excluded.commit_start_datetime;"""
        execute_sql = True
    elif call_commit.get_action_class() is ActionClass.MOVE:
        logging.debug(
            "TODO, check if calling function is the same, else set end and insert: %s",
            call_commit.get_action_class(),
        )
    else:
        logging.error(
            "not valid Commit ActionClass: %s", call_commit.get_action_class()
        )

    if execute_sql:
        cur.execute(sql_string)
        con_analytics_db.commit()
    else:
        logging.warning(
            "Nothing to insert call_commit: %s", call_commit.get_action_class()
        )


# def save_call_commit_rows(Bs_tree, proj_paths: ProjectPaths, commit: Commit):
#     data = np.array([[2014,"toyota","corolla"],
#                  [2018,"honda","civic"],
#                  [2020,"hyndai","accent"],
#                  [2017,"nissan","sentra"]])
#
#     # pass column names in the columns parameter
#     df = pd.DataFrame(data, columns = ['year', 'make','model'])
#
#     # save to database
#     con_analytics_db = sqlite3.connect(path_to_project_db)
#     cur = con_analytics_db.cursor()


def save_call_commit_rows() -> None:
    logging.info("TODO")
    print("TODO")


def save_funciton_call_rows() -> None:
    logging.info("TODO")
    print("TODO")


def save_raw_function_call_curr_rows(
    path_to_project_db: str, rows: List[ExtendedFunctionCall], mod_file_data: FileData
) -> None:
    """
    If row already exists then only the hash_start and start_date will be updated, else if not exists insert.
    Closed is only set if row did not exist previously.

    Parameters:
    rows (list[tuple[str..]]): Array of form ([calling_function_unqualified_name,calling_function_nr_parameters,called_function_unqualified_name,
    commit_hash_start,  commit_start_datetime, commit_hash_oldest, commit_oldest_datetime, commit_hash_end, commit_end_datetime, closed],...[])

    """
    try:
        con_analytics_db = sqlite3.connect(path_to_project_db)
        cur = con_analytics_db.cursor()

        for fc in rows:
            # logging.debug("Updating {0},{1},{2},{3},{4}".format(
            #    mod_file_data.get_file_path(), fc[0], fc[1], fc[2], fc[4]))
            # update start_hash if raw_function_call already existing and start_hash is not earlier as current hash
            sql_string = f"""UPDATE raw_function_call SET
                        commit_hash_start='{fc[3]}', commit_start_datetime='{fc[4]}',
                        commit_hash_oldest='{fc[5]}', commit_oldest_datetime='{fc[6]}'
                        WHERE
                        file_path='{mod_file_data.get_file_path()}'
                        AND calling_function_unqualified_name='{fc[0]}'
                        AND calling_function_nr_parameters = {fc[1]}
                        AND called_function_unqualified_name = '{fc[2]}'
                        AND closed = 0
                        AND DATE(commit_start_datetime) >= DATE('{fc[4]}');"""

            cur.execute(sql_string)

            # raw_function_call did not previously exist, then insert only with start hash values
            if cur.rowcount <= 0:
                # logging.debug("No previous record, insert.")
                sql_string = f"""INSERT INTO raw_function_call
                            (file_name, file_dir_path, file_path,
                            calling_function_unqualified_name, calling_function_nr_parameters,
                            called_function_unqualified_name,
                            commit_hash_start, commit_start_datetime,
                            commit_hash_oldest, commit_oldest_datetime,
                            closed)
                        VALUES (
                            '{mod_file_data.get_file_name()}','{mod_file_data.get_file_dir_path()}','{mod_file_data.get_file_path()}',
                            '{fc[0]}',{fc[1]},'{fc[2]}','{fc[3]}','{fc[4]}','{fc[5]}','{fc[6]}',0
                        );"""
                cur.execute(sql_string)

        con_analytics_db.commit()
        cur.close()
    except sqlite3.Error as err:
        con_analytics_db.rollback()
        cur.close()
        logging.error(
            "An exception of type %s occurred. Arguments:\n%s",
            type(err).__name__,
            repr(err.args),
        )


def save_raw_function_call_deleted_rows(
    path_to_project_db: str, rows: List[ExtendedFunctionCall], mod_file_data: FileData
) -> None:
    """
    Closed is only set if row did not exist previously.
    If row already exists then only the hash_start and start_date will be updated.

    Parameters:
    rows (list[tuple[str..]]): Array of form ([calling_function_unqualified_name,calling_function_nr_parameters,called_function_unqualified_name,
    commit_hash_start,  commit_start_datetime, commit_hash_oldest, commit_oldest_datetime, commit_hash_end, commit_end_datetime, closed],...[])

    """
    con_analytics_db = sqlite3.connect(path_to_project_db)
    cur = con_analytics_db.cursor()
    try:
        for fc in rows:
            sql_string = f"""UPDATE raw_function_call SET
                        commit_hash_end='{fc[6]}', commit_end_datetime='{fc[7]}', closed = 1
                        WHERE
                        file_path='{mod_file_data.get_file_path()}'
                        AND calling_function_unqualified_name='{fc[0]}'
                        AND calling_function_nr_parameters = {fc[1]}
                        AND called_function_unqualified_name = '{fc[2]}'
                        AND closed = 0;"""
            # logging.debug(sql_string)
            cur.execute(sql_string)
            logging.debug("cur.rowcount %s", cur.rowcount)

            # raw_function_call did not previously exist, then insert only with end hash values
            if cur.rowcount <= 0:
                logging.debug(
                    "Del func_call not previously existing: %s,%s,%s",
                    fc[0],
                    fc[1],
                    fc[2],
                )
                sql_string = f"""INSERT INTO raw_function_call
                            (file_name, file_dir_path, file_path,
                            calling_function_unqualified_name, calling_function_nr_parameters,
                            called_function_unqualified_name,
                            commit_hash_oldest, commit_oldest_datetime,
                            commit_hash_end, commit_end_datetime, closed)
                        VALUES (
                            '{mod_file_data.get_file_name()}','{mod_file_data.get_file_dir_path()}','{mod_file_data.get_file_path()}',
                            '{fc[0]}',{fc[1]},'{fc[2]}','{fc[7]}','{fc[6]}','{fc[7]}','{fc[6]}',1)
                        ON CONFLICT (file_path, calling_function_unqualified_name, calling_function_nr_parameters, called_function_unqualified_name,
                            commit_hash_start, commit_hash_oldest, commit_hash_end)
                        DO UPDATE SET commit_hash_oldest=excluded.commit_hash_oldest,
                            commit_oldest_datetime=excluded.commit_oldest_datetime,
                            commit_hash_end = excluded.commit_hash_end,
                            commit_end_datetime = excluded.commit_end_datetime,
                            closed = excluded.closed;"""
                # logging.debug(sql_string)
                cur.execute(sql_string)

        con_analytics_db.commit()
        cur.close()
    except sqlite3.Error as err:
        con_analytics_db.rollback()
        cur.close()
        logging.error(
            "An exception of type %s occurred. Arguments:\n%s",
            type(err).__name__,
            repr(err.args),
        )


def complete_function_calls_data(
    _arr_function_calls: List[ExtendedFunctionCall],
) -> None:
    """
    if not existing completes the long_name, name and parameters of the given functions
    """
    logging.info("TODO")
    print("TODO")
