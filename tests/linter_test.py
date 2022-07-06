import os
import subprocess
from typing import Sequence, NamedTuple
from pathlib import Path

import pytest


_ROOT_DIR = Path(__file__).parent.parent


# use a separate linter to get readable test names
@pytest.mark.parametrize(
    "linter,options",
    [
        # linters
        ("pylint", ["CCSD", "tests"]),
        ("flake8", ["."]),
        # type checker
        ("mypy", ["."]),
        # find vulnerable dependencies
        ("safety", ["check", "--full-report"]),
    ],
)
@pytest.mark.linter
def test_linter(linter: str, options: Sequence[str]) -> None:
    command = [linter, *options]
    print(" ".join(command))
    result = _run(command)
    print(os.linesep.join([result.stdout, result.stderr]))
    assert result.exit_code == 0


_RunResult = NamedTuple(
    "_RunResult",
    [
        ("exit_code", int),
        ("stdout", str),
        ("stderr", str),
    ],
)


def _run(command: Sequence[str]) -> _RunResult:
    with subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(_ROOT_DIR)
    ) as proc:
        stdout, stderr = proc.communicate()
        return _RunResult(
            exit_code=proc.returncode,
            stdout=stdout.decode("utf-8"),
            stderr=stderr.decode("utf-8"),
        )
