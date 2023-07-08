from __future__ import annotations

from efs.core.path_core import (convert_path_to_unix, convert_path_to_windows,
                                expand_relative_path,
                                find_parent_sibling_from_path,
                                get_current_working_directory,
                                get_file_extension, get_file_name_no_extension,
                                get_file_name_with_extension, get_file_path,
                                get_file_path_absolute, get_node_at,
                                get_parent, get_path_parts_and_extension,
                                get_path_parts_no_extension,
                                get_temp_directory, get_user_directory,
                                is_absolute, is_unix_like, is_windows_like,
                                join, remove_extension,
                                remove_file_name_from_path_if_is_file,
                                replace_extension,
                                set_current_working_directory, set_node_at,
                                split, strip_path_up_to_node_name,
                                strip_path_up_to_node_name_reversed)

__all__ = [
    "join",
    "split",
    "get_node_at",
    "set_node_at",
    "is_absolute",
    "is_unix_like",
    "is_windows_like",
    "convert_path_to_windows",
    "convert_path_to_unix",
    "get_file_path",
    "get_file_path_absolute",
    "get_file_extension",
    "get_file_name_with_extension",
    "get_file_name_no_extension",
    "get_path_parts_and_extension",
    "get_path_parts_no_extension",
    "remove_file_name_from_path_if_is_file",
    "expand_relative_path",
    "get_user_directory",
    "get_temp_directory",
    "get_current_working_directory",
    "set_current_working_directory",
    "remove_extension",
    "get_parent",
    "find_parent_sibling_from_path",
    "strip_path_up_to_node_name",
    "strip_path_up_to_node_name_reversed",
    "replace_extension",
    "Path",
    "PathLike",
    "from_path_like",
]


class Path:
    __slots__ = "_path"

    def __init__(self, initial_path: str = ""):
        if initial_path is None:
            raise ValueError("Path cannot be null")

        self._path: str = initial_path

    @classmethod
    def from_user_directory(cls) -> Path:
        return cls(get_user_directory())

    @classmethod
    def from_temp_directory(cls) -> Path:
        return cls(get_temp_directory())

    @classmethod
    def from_current_working_directory(cls) -> Path:
        return cls(get_current_working_directory())

    @classmethod
    def from_find_parent_sibling_in_path(cls, path: str, sibling_name: str) -> Path:
        return cls(find_parent_sibling_from_path(path, sibling_name))

    # Properties
    @property
    def path(self) -> str:
        return self._path

    @property
    def split(self) -> list[str]:
        return split(self._path)

    @property
    def is_absolute(self) -> bool:
        return is_absolute(self._path)

    @property
    def is_unix_like(self) -> bool:
        return is_unix_like(self._path)

    @property
    def is_windows_like(self) -> bool:
        return is_windows_like(self._path)

    @property
    def get_file_path(self) -> str:
        return get_file_path(self._path)

    @property
    def get_file_path_absolute(self) -> str:
        return get_file_path_absolute(self._path)

    @property
    def get_file_extension(self) -> str:
        return get_file_extension(self._path)

    @property
    def get_file_name_with_extension(self) -> str:
        return get_file_name_with_extension(self._path)

    @property
    def get_file_name_no_extension(self) -> str:
        return get_file_name_no_extension(self._path)

    @property
    def get_path_parts_and_extension(self) -> tuple[str | None, ...]:
        return get_path_parts_and_extension(self._path)

    @property
    def get_path_parts_no_extension(self) -> tuple[str | None, ...]:
        return get_path_parts_no_extension(self._path)

    def get_node_at(self, index: int) -> str:
        return get_node_at(self._path, index)

    def find_parent_sibling_from_path(self, sibling_name: str) -> str | None:
        return find_parent_sibling_from_path(self._path, sibling_name)

    # Modifiers
    def join(self, *elements: str) -> Path:
        self._path = join(self._path, *elements)
        return self

    def convert_path_to_windows(self) -> Path:
        self._path = convert_path_to_windows(self._path)
        return self

    def convert_path_to_unix(self) -> Path:
        self._path = convert_path_to_unix(self._path)
        return self

    def remove_file_name_from_path_if_is_file(self) -> Path:
        self._path = remove_file_name_from_path_if_is_file(self._path)
        return self

    def expand_relative_path(self) -> Path:
        self._path = expand_relative_path(self._path)
        return self

    def swap_current_working_directory(self) -> Path:
        temp: str = self._path
        self._path = get_current_working_directory()
        set_current_working_directory(temp)
        return self

    def set_as_current_working_directory(self) -> Path:
        set_current_working_directory(self._path)
        return self

    def remove_extension(self) -> Path:
        self._path = remove_extension(self._path)
        return self

    def move_to_parent(self) -> Path:
        self._path = get_parent(self._path)
        return self

    def strip_path_up_to_node_name(self, node_name: str, inclusive: bool = False) -> Path:
        self._path = strip_path_up_to_node_name(self._path, node_name, inclusive=inclusive)
        return self

    def strip_path_up_to_node_name_reversed(self, node_name: str, inclusive: bool = False) -> Path:
        self._path = strip_path_up_to_node_name_reversed(self._path, node_name, inclusive=inclusive)
        return self

    def replace_extension(self, with_: str) -> Path:
        self._path = replace_extension(self._path, with_)
        return self

    def set_node_at(self, index: int, new_name: str) -> Path:
        self._path = set_node_at(self._path, index, new_name)
        return self

    def __eq__(self, other) -> bool:
        return isinstance(other, Path) and other.path == self._path

    def __ne__(self, other) -> bool:
        return not self == other

    def __repr__(self) -> str:
        return f'Path(path="{self._path}")'


PathLike = str | Path


def from_path_like(path: PathLike) -> str:
    return path.path if isinstance(path, Path) else path
