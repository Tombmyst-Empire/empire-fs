"""
FS Path manipulation tools.

For this module, a path is constituted of:

- **Separators**: ``\`` in Windows, ``/`` everywhere else
- **Nodes**: Each name in the path, that represents either a directory or a file. Each is separated by *separators*
- **Directory**: A folder
- **Extension**: Everything that follows the last dot (``.``) of a filename, and that dot must not starts the filename.
"""

def join(*args: str) -> str | None: ...
def split(path: str) -> list[str]: ...
def is_absolute(path: str) -> bool: ...
def is_unix_like(path: str) -> bool: ...
def is_windows_like(path: str) -> bool: ...
def convert_path_to_windows(path: str) -> str | None: ...
def convert_path_to_unix(path: str) -> str | None: ...
def get_file_path(path: str) -> str | None:
    """
    Removes the file name from *path* or the last path element
    """

def get_file_path_absolute(path: str) -> str | None:
    """
    Similar to ``get_file_path``, but also expands the path to an absolute one
    """

def get_file_extension(path: str) -> str | None: ...
def get_file_name_with_extension(path: str) -> str | None: ...
def get_file_name_no_extension(path: str) -> str | None: ...
def get_path_parts_and_extension(path: str) -> tuple[str | None, ...]:
    """
    Returns a tuple where indices:

        - 0 = path
        - 1 = file name
        - 2 = extension
    """

def get_path_parts_no_extension(path: str) -> tuple[str | None, ...]:
    """
    Returns a tuple where indices:

    - 0 = path
    - 1 = file name
    """

def remove_file_name_from_path_if_is_file(path: str) -> str | None:
    """
    Removes a real file name (it must exists) from *path*
    """

def expand_relative_path(path: str) -> str | None: ...
def get_user_directory() -> str: ...
def get_temp_directory() -> str: ...
def get_current_working_directory() -> str: ...
def set_current_working_directory(path: str): ...
def remove_extension(path: str) -> str | None: ...
def get_parent(path: str) -> str | None: ...
def find_parent_sibling_from_path(path: str, name: str) -> str | None:
    """
    Looks for *name*, which can be a file or a directory, in *path* and its parent directories.

    If not found, returns None.
    """

def strip_path_up_to_node_name(path: str, node_name: str, *, inclusive: bool = False) -> str | None:
    """
    Removes every nodes until the first occurrence of *node_name* from *path*, reading from left to
    right. If not found, *path* is returned.

    If *inclusive*, then *node_name* will be inserted in the result.
    """

def strip_path_up_to_node_name_reversed(path: str, node_name: str, *, inclusive: bool = False) -> str | None:
    """
    Removes every nodes until the first occurrence of *node_name* from *path*, reading from right to
    left. If not found, *path* is returned.

    If *inclusive*, then *node_name* will be inserted in the result.
    """

def replace_extension(path: str, with_: str) -> str | None: ...
def get_node_at(path: str, index: int) -> str:
    """
    Returns the node of *path* at *index*.
    :raises IndexError if *index* greater than the number of nodes
    """

def set_node_at(path: str, index: int, new_node: str) -> str: ...
