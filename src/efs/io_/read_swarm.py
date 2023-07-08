from __future__ import annotations

import atexit
from typing import Any, BinaryIO, Generic, TextIO, Type, TypeVar

T = TypeVar("T")


class ReadSwarm(Generic[T]):
    """
    Reads multiple files at once
    """

    __slots__ = ("_files", "_file_handles", "_container_type")

    def __init__(self, *files: str, container_type: Type[T] | None = None):
        """
        Open each *files* for read.

        If *container_type*, when a line is read from the swarm, an instance of *container_type* will
        be created and each of its field will be assigned **in the same order as the provided *files***.
        Ideally, this parameter should be a dataclass or any other class with a proper __init__ method.

        If *container_type* is not provided, the read files will return a tuple instead for each line read.
        """
        self._files: tuple[str] = files
        self._file_handles: dict[str, TextIO | BinaryIO] = {}
        self._container_type: Type[T] | None = container_type
        atexit.register(self.close)

    def __enter__(self) -> ReadSwarm:
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        for f in self._files:
            self._file_handles[f] = open(f, "r", encoding="utf8")

    def read_line(self) -> T | tuple[str] | None:
        items: tuple[str | None] = tuple(self._read_line_or_default(f) for f in self._file_handles.values())
        if not any(items):
            return None

        if self._container_type:
            return self._container_type(*items)
        else:
            return items

    def _read_line_or_default(self, f: TextIO | BinaryIO, default: Any = None) -> str | None:
        try:
            return f.readline()
        except Exception:
            return default

    def close(self):
        for f in self._file_handles.values():
            try:
                f.close()
            except Exception:
                pass
