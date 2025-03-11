# %%
import os
import subprocess
from subprocess import Popen, PIPE
from typing import Any, Callable, List, Tuple
import logging

from importlib import reload

from .models import ExtendedFunctionCall, FileData, FileImport, CallCommitInfo, CommitDates, FunctionCall
from . import utils_py, models, utils_sql

# %%
reload(utils_sql)
reload(models)


# %%
# os.environ['COMSPEC']

# %%
# con.close()

# %%
# Functions


def save_source_code(file_path: str, source_text: str) -> None:
    """
    Creates the dir and file if not existed.
    """
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    if source_text is None:
        return

    if isinstance(source_text, bytes):
        logging.debug("save_source_code was bytes")
        source_text = source_text.decode('utf-8')

    try:
        f = open(file_path, 'w', encoding='utf-8')  # pylint: disable=consider-using-with
    except OSError:
        logging.error("could not open/write file: %s", file_path)

    try:
        f.writelines(source_text)
    except UnicodeEncodeError:
        # some pydriller.commit.mod_file.source_text has encoding differences
        print("ERROR writelines", type(source_text))
        logging.warning("ERROR writelines %s", type(source_text))
        f.write(source_text.encode('utf-8-sig'))  # type: ignore[arg-type]
    except OSError as err:
        logging.error(file_path)
        logging.exception(err)
    f.close()
    save_source_code_xml(file_path)


def delete_source_code(file_path: str) -> None:
    if os.path.isfile(file_path):
        os.remove(file_path)
    else:  # Show an error
        logging.debug("Error: %s file not found", file_path)


def delete_empty_dir(dir_path: str) -> None:
    # dir_path = os.path.dirname(file_path)
    if os.path.isdir(dir_path):
        if not os.listdir(dir_path):
            logging.debug("Delete directory, it became empty")
        else:
            logging.debug("Directory is not empty")
    else:
        logging.error("Directory doesn't exist %s", dir_path)


def save_source_code_xml(file_path: str) -> None:
    try:
        _command_output_to_file(['srcml', file_path], f'{file_path}.xml')
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logging.warning("srcml not found or failed. Skipping XML conversion. Error: %s", str(e))
        # Create an empty XML file as placeholder to prevent repeated attempts
        with open(f'{file_path}.xml', 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<unit/>')


def save_source_code_diff_file(arg_prev: str, arg_curr: str, arg_target_file: str) -> None:
    _command_output_to_file(['gumtree', 'textdiff', arg_prev, arg_curr], arg_target_file)


def _command_output_to_file(args: List[str], target_file: str) -> None:
    with open(target_file, 'w', encoding='utf-8') as file:
        subprocess.run(args, check=True, stdout=file)


def save_compact_xml_parsed_code(path_to_cache_dir: str, relative_file_path: str, source_text: str) -> None:
    local_file_path = os.path.join(path_to_cache_dir, relative_file_path)

    if not os.path.exists(os.path.dirname(local_file_path)):
        os.makedirs(os.path.dirname(local_file_path))

    if isinstance(source_text, bytes):
        logging.debug("save_source_code was bytes")
        source_text = source_text.decode('utf-8')

    try:
        f = open(local_file_path, 'w', encoding='utf-8')  # pylint: disable=consider-using-with
    except OSError:
        logging.error("could not open/write file: %s", local_file_path)

    try:
        f.writelines(source_text)
    except UnicodeEncodeError:
        # some pydriller.commit.mod_file.source_text has encoding differences
        print("ERROR writelines", type(source_text))
        logging.warning("ERROR writelines %s", type(source_text))
        f.write(source_text.encode('utf-8-sig'))  # type: ignore[arg-type]
    except OSError as err:
        logging.error(relative_file_path)
        logging.exception(err)
    f.close()


def is_java_file(mod_file: str) -> bool:
    return mod_file[-5:] == '.java'


def is_cpp_file(mod_file: str) -> bool:
    # or mod_file[-2:] == '.h'
    return mod_file[-4:] == '.cpp' or mod_file[-2:] == '.c'


def is_python_file(mod_file: str) -> bool:
    return mod_file[-3:] == '.py'


_FILE_TYPE_VALIDATION_FUNCTIONS = {
    'java': is_java_file,
    'cpp': is_cpp_file,
    'python': is_python_file,
}


def get_file_type_validation_function(proj_lang: str) -> Callable[[str], bool]:
    return _FILE_TYPE_VALIDATION_FUNCTIONS[proj_lang]


def get_file_imports(proj_lang: str, path_to_src_files: str, source_code: str, mod_file_data: FileData) -> List[FileImport]:
    if source_code is None or len(source_code) == 0:
        logging.warning("sourcecode is empty.")
        return []

    if proj_lang == 'cpp':
        return get_file_imports_cpp(source_code, mod_file_data)
    if proj_lang == 'java':
        return get_file_imports_java(
            path_to_src_files, source_code, mod_file_data)
    return []


def get_file_imports_cpp(source_code: str, mod_file_data: FileData) -> List[FileImport]:
    count = 0
    imports = []
    for code_line in source_code.splitlines():
        count += 1
        if count < 500:
            if (code_line.lstrip()).startswith("#include "):
                f_name, f_path, f_dir_path, f_file_pkg = get_import_file_data_cpp(
                    mod_file_data.get_file_dir_path(), code_line)

                imports.append(FileImport(
                    src_file_data=mod_file_data,
                    import_file_path=f_path,
                    import_file_name=f_name,
                    import_file_dir_path=f_dir_path,
                    import_file_pkg=f_file_pkg,
                ))
        else:
            break

    return imports


def get_file_imports_java(path_to_src_files: str, source_code: str, mod_file_data: FileData) -> List[FileImport]:
    count = 0
    imports = []
    for code_line in source_code.splitlines():
        count += 1
        if count < 500:
            if (code_line.lstrip()).startswith("import "):
                f_name, f_path, f_dir_path, f_file_pkg = get_import_file_data_java(
                    path_to_src_files, code_line)

                imports.append(FileImport(
                    src_file_data=mod_file_data,
                    import_file_path=f_path,
                    import_file_name=f_name,
                    import_file_dir_path=f_dir_path,
                    import_file_pkg=f_file_pkg,
                ))
        else:
            break

    return imports


def get_import_file_data_cpp(mod_file_dir_path: str, code_line: str) -> Tuple[str, str, str, None]:
    """
    e.g. #include <QDebug> or #include "jkqtplotter/jkqtpbaseplotter.h"
    """
    f_name = ''
    f_dir_path = ''
    f_path = code_line[9:len(code_line.rstrip())].replace('"', '')
    f_path = f_path.replace('<', '')
    f_path = f_path.replace('>', '')
    f_name = os.path.basename(f_path)

    # includes libraries eg. <cmath> <QApplication>
    if code_line.__contains__('<'):
        f_name = f_path

    if (code_line.__contains__('"') and not code_line.__contains__('/')):
        f_dir_path = mod_file_dir_path
        f_name = f_path
    else:
        f_dir_path = os.path.dirname(f_path)
    return f_name, f_path, f_dir_path, None


def get_import_file_data_java(path_to_src_files: str, code_line: str) -> Tuple[str, str, str, str]:
    """
    format import pkg1[.pkg2].(classname|*);

    :param

    :return: f_name - the name of the classname
    :return: f_path - the likely path if the import contained a classname
    :return: f_dir_path - the path to the directory of the pkg
    :return: f_pkg - the pkg

    """
    f_name = ''
    f_dir_path = ''
    f_path = ''  # TODO GGG correct
    f_pkg = ''
    f_pkg = code_line[7:len(code_line.rstrip())].replace(';', '')
    chunks = f_pkg.split(".")
    f_name = chunks[len(chunks)-1]

    # java specific
    if path_to_src_files is not None:
        f_dir_path = os.path.normpath(path_to_src_files)
        chunks = f_pkg.split('.')
        for chunk in chunks[:-1]:
            f_dir_path = os.path.join(f_dir_path, chunk)

        if not code_line.__contains__('*'):
            f_path = os.path.join(f_dir_path, ''.join(
                [chunks[-1].split('.')[-1], '.java']))
        else:
            f_path = f_dir_path
    return f_name, f_path, f_dir_path, f_pkg


def jar_wrapper(*args: str) -> List[bytes]:
    with Popen(['java', '-jar', *args], stdout=PIPE, stderr=PIPE) as process:
        assert process.stdout is not None
        ret = []
        while process.poll() is None:
            line = process.stdout.readline()
            if line != b'' and line.endswith(b'\n'):
                ret.append(line[:-1])
        stdout, stderr = process.communicate()
        ret += stdout.split(b'\n')
        if stderr != b'':
            ret += stderr.split(b'\n')
        ret.remove(b'')
        return ret


def read_xml_diffs_from_file(_file_path: str) -> None:
    # read xml in case saved on file
    # with open(file_path, 'r') as f:
    #     data = f.read()
    pass


def get_calls(raw: str) -> None:
    indents = [(0, 0, 'root')]
    for line in raw.split('\n'):
        indent = 0
        while line[indent] == ' ':
            indent += 1
        if indent % 4:
            print("not multiple of 4")
            break
        cnt = line.replace('  ', '')
        cnt = cnt.split("[", -1)[0]
        indents.append((len(indents), int(indent/4)+1, cnt))
    for ident in indents:
        print(ident)


def parse_xml_call_diffs(  # type: ignore[misc]
    diff_xml_file: Any, path_to_cache_current: str, mod_file_data: FileData,
) -> List[CallCommitInfo]:
    imports = []
    try:
        f_name = diff_xml_file.dstFile.get_text()
        # TODO check how path is written
        f_name = f_name.replace(path_to_cache_current, '')
        logging.debug("Dest file name: %s", f_name)

        for action in diff_xml_file.find_all('action'):
            logging.debug('---action node----')
            action_node_type = action.actionNodeType.get_text()
            logging.debug("Action node type: %s", action_node_type)
            action_class = utils_py.get_action_class(action.actionClassName.get_text())
            logging.debug("CHECK Action class: %s, action_class: %s ", action.actionClassName.get_text(), action_class)
            handled = action.handled.get_text()
            logging.debug("Handled: %s", handled)
            parent_function_name = action.parentFunction.get_text()
            logging.debug("Parent: %s", parent_function_name)
            action_calls = action.calls
            logging.debug("action_calls: %s", action_calls)

            for ncall in action.calls.find_all('callName'):
                logging.debug(ncall.get_text())
                called_function_name = ncall.get_text()
                cci = CallCommitInfo(src_file_data=mod_file_data,
                                     calling_function=parent_function_name,
                                     called_function=called_function_name,
                                     action_class=action_class)
                imports.append(cci)
                # get_calls(at.get_text())
    except Exception as err:  # pylint: disable=broad-except
        logging.exception(err)
    return imports


def save_call_commit_rows() -> None:
    logging.info("TODO")
    print("TODO")


def get_unqualified_name(base_name: str) -> str:
    if base_name.__contains__('::'):
        return (base_name).split(
            '::')[len((base_name).split('::'))-1]
    return base_name


def set_hashes_to_function_calls(
    curr_function_calls: List[FunctionCall], prev_function_calls: List[FunctionCall], cm_dates: CommitDates,
) -> Tuple[List[ExtendedFunctionCall], List[ExtendedFunctionCall]]:
    """
    Returns an array of rows that contain the function_call's to be insterted in the database,
    including the hash_start and hash_end and dates.

    Curr Commit can update start_hash from all present functions, if no older start_hash(date)  exists and no previous end_hash(date) exists.
    Curr Commit can update(with insert if necessary) the end_hash from functions known to be deleted with curr commit, if the function is not closed.

    Parameters:
    curr_function_calls (list[tuple[str..]]): Array of form ([calling_function_unqualified_name,
        calling_function_nr_parameters,called_function_unqualified_name],...[])
    prev_function_calls (list[tuple[str..]]): Array of form ([calling_function_unqualified_name,
        calling_function_nr_parameters,called_function_unqualified_name],...[])
    cm_dates (CommitDates): Dates of the current commit.
    deleted_functions_names (list[tuple[str]]): Array of form ([f.long_name, f.unqualified_name]...[])

    Returns:
    rows_curr (list[tuple[str...]]): Array of form ([calling_function_unqualified_name,calling_function_nr_parameters,
        called_function_unqualified_name,commit_hash_start,  commit_start_datetime, commit_hash_oldest, commit_oldest_datetime, commit_hash_end,
        commit_end_datetime, closed],...[])
    rows_deleted (list[tuple[str..]]): Same structure as rows_curr

    """

    # commit_previous_functions = [
    #     (f.long_name, get_unqualified_name(f.name)) for f in mod_file.methods_before]
    # commit_current_functions = [
    #     (f.long_name, get_unqualified_name(f.name)) for f in mod_file.methods]
    # commit_changed_functions = [
    #     (f.long_name, get_unqualified_name(f.name)) for f in mod_file.changed_methods]

    # Calling functions
    # get added functions (existing in curr but not prev)
    # added_functions = list(
    #     set(commit_current_functions) - set(commit_previous_functions))
    # get deleted functions (existing in prev but not in curr)
    # deleted_functions = list(
    #     set(commit_previous_functions) - set(commit_current_functions))
    # get just changed functions
    # changed_functions = list(
    #     set(commit_changed_functions) - set(added_functions) - set(deleted_functions))
    # get not changed functions
    # unchanged_functions = list(
    #     set(commit_previous_functions).intersection(commit_current_functions) - set(changed_functions))

    logging.debug("PREV FUNCTION CALLS Qty: %d", len(prev_function_calls))
    logging.debug("CURR FUNCTION CALLS Qty: %d", len(curr_function_calls))

    # Called functions
    added_calls = list(set(curr_function_calls) - set(prev_function_calls))
    deleted_calls = list(set(prev_function_calls) - set(curr_function_calls))
    unchanged_calls = list(
        set(prev_function_calls).intersection(curr_function_calls))

    rows_curr: List[ExtendedFunctionCall] = []

    for calls in added_calls:
        rows_curr.append(ExtendedFunctionCall(
            *calls, cm_dates.get_commit_hash(), cm_dates.get_commiter_datetime(),
            cm_dates.get_commit_hash(), cm_dates.get_commiter_datetime(), None, None, 0,
        ))
    for calls in unchanged_calls:
        rows_curr.append(ExtendedFunctionCall(
            *calls, None, None, cm_dates.get_commit_hash(),
            cm_dates.get_commiter_datetime(), None, None, 0,
        ))

    rows_deleted: List[ExtendedFunctionCall] = []
    for calls in deleted_calls:
        rows_deleted.append(ExtendedFunctionCall(
            *calls, None, None, cm_dates.get_commit_hash(), cm_dates.get_commiter_datetime(),
            cm_dates.get_commit_hash(), cm_dates.get_commiter_datetime(), 1,
        ))

    logging.debug("added_calls qty %d", len(added_calls))
    logging.debug("unchanged_calls qty %d", len(unchanged_calls))
    logging.debug("deleted_calls qty %d", len(deleted_calls))

    return rows_curr, rows_deleted
