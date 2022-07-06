from typing import Callable, Generic, List, Tuple, TypeVar

from .canvas import Signature
from .result import GroupResult


class Task:
    pass


_T = TypeVar('_T')


class _GenericTask(Generic[_T], Task):
    def signature(self, args: _T) -> Signature: ...


_T1 = TypeVar('_T1')
_T2 = TypeVar('_T2')
_T3 = TypeVar('_T3')


class Celery:
    def __init__(self, include: List[str] = ...) -> None: ...

    def task(self) -> Callable[[Callable[[_T1, _T2, _T3], None]], _GenericTask[Tuple[_T1, _T2, _T3]]]: ...


class group(Signature):
    def __init__(self, *tasks: Signature | List[Signature]) -> None: ...

    def apply_async(self) -> GroupResult: ...
