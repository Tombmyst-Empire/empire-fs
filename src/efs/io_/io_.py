from __future__ import annotations

import atexit
import contextlib
from abc import ABC, abstractmethod
from enum import Enum, IntEnum
from typing import Any, BinaryIO, Callable, Generic, TextIO, Type, TypeVar

from empire_commons.exceptions.exceptions import UnexpectedCoreException

T = TypeVar("T")


class BufferingEnum(IntEnum):
    DEFAULT = 8192
    OFF = 0
    LINE_BUFFERING = 1


class StartLocationsEnum(Enum):
    START_OF_FILE_NO_TRUNCATE = "r+"
    START_OF_FILE_TRUNCATE = "w+"
    END_OF_FILE = "a+"


class _OpenFileBase(ABC):
    __slots__ = (
        "_file_path",
        "_file_object",
        "_buffering",
        "_encoding",
        "_newline",
        "_binary",
    )

    def __init__(
        self,
        path: str,
        buffering: int | BufferingEnum = BufferingEnum.DEFAULT,
        encoding: str = "utf8",
        newline: str = "\n",
        binary: bool = False,
    ):
        self._file_path: str = path
        self._file_object: Any = None

        self._buffering: int | BufferingEnum = buffering
        self._encoding: str = encoding
        self._newline: str = newline
        self._binary: bool = binary

        atexit.register(_OpenFileBase._close, self)

    def __del__(self):
        self._close()

    @abstractmethod
    def __enter__(self):
        raise NotImplementedError()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()

    def _open(self, mode: str) -> TextIO | BinaryIO:
        if self._binary:
            mode += "b"

        self._file_object = open(
            self._file_path,
            mode,
            buffering=self._buffering,
            encoding=self._encoding,
            newline=self._newline,
        )

        if not self._file_object:
            raise UnexpectedCoreException(f'Could not open file {self._file_path} as {mode} with encoding "utf8": _file_object is None')

        return self._file_object

    def _close(self):
        if self._file_object:
            with contextlib.suppress(Exception):
                self._file_object.close()


class OpenFileForRead(_OpenFileBase):
    def __enter__(self):
        return super()._open("r")

    def open(self) -> TextIO | BinaryIO:
        return super()._open("r")


class OpenFileForWrite(_OpenFileBase):
    def __enter__(self):
        return super()._open("w")

    def open(self) -> TextIO | BinaryIO:
        return super()._open("w")


class OpenFileForAppend(_OpenFileBase):
    def __enter__(self):
        return super()._open("a")

    def open(self) -> TextIO | BinaryIO:
        return super()._open("a")


class OpenFileForRandom(_OpenFileBase):
    __slots__ = ("_starting_location",)

    def __init__(
        self,
        starting_location: StartLocationsEnum,
        path: str,
        buffering: int | BufferingEnum = BufferingEnum.DEFAULT,
        encoding: str = "utf8",
        newline: str = "\n",
        binary: bool = False,
    ):
        super().__init__(
            path=path,
            buffering=buffering,
            encoding=encoding,
            newline=newline,
            binary=binary,
        )
        self._starting_location: StartLocationsEnum = starting_location

    def __enter__(self):
        try:
            return super()._open(self._starting_location.value())
        except FileExistsError:
            pass

    def open(self) -> BinaryIO:
        try:
            return super()._open(self._starting_location.value())
        except FileExistsError:
            pass


class CreateFileIfNotExists(_OpenFileBase):
    def __enter__(self):
        try:
            return super()._open("x")
        except FileExistsError:
            pass

    def open(self) -> TextIO | BinaryIO:
        try:
            return super()._open("x")
        except FileExistsError:
            pass


def file_lines_iterate(file: str, callback: Callable[[int, str], None]):
    """
    For each line read from *file*, *callback* will be called with line number (starting at 0) and line text
    """
    with OpenFileForRead(file) as f:
        for index, line in enumerate(f):
            callback(index, line)
