"""
A facade against multiple functions to behave on the file system
"""
import gzip
import os
import shutil
from contextlib import contextmanager
from datetime import datetime
from enum import Enum, IntEnum
from os import path as os_path
from typing import Any, BinaryIO, Generator, TextIO

from empire_commons.on_error import OnError, catch, handle_error
from empire_commons.os_util import os_name

from efs.core.path_core import get_path_parts_and_extension, join
from efs.path.path_class import PathLike, from_path_like

__all__ = [
    "BufferingEnum",
    "copy_directory",
    "copy_file",
    "count_lines",
    "create_file",
    "delete_file",
    "exists",
    "get_file_creation_datetime",
    "get_file_last_access_datetime",
    "get_file_last_modified_datetime",
    "get_file_size",
    "get_next_available_file_name",
    "is_directory",
    "is_file",
    "is_link",
    "is_mount",
    "make_hard_link",
    "make_symlink",
    "merge_files",
    "mkdir",
    "move_directory",
    "move_file",
    "open_append",
    "open_random",
    "open_read",
    "open_write",
    "remake_dir",
    "rename",
    "rmdir",
    "StartLocationsEnum",
    "ungzip_to_text",
]

from empire_commons.functions import coalesce, maybe_enum


class BufferingEnum(IntEnum):
    DEFAULT = 8192
    OFF = 0
    LINE_BUFFERING = 1


class StartLocationsEnum(Enum):
    START_OF_FILE_NO_TRUNCATE = "r+"
    START_OF_FILE_TRUNCATE = "w+"
    END_OF_FILE = "a+"


@catch(default_on_error_behavior=OnError.IGNORE, value_to_return_on_error=False)
def exists(path: PathLike) -> bool:
    return is_file(path) or is_directory(path)


@catch(default_on_error_behavior=OnError.IGNORE, value_to_return_on_error=False)
def is_file(path: PathLike) -> bool:
    return os_path.isfile(from_path_like(path))


@catch(default_on_error_behavior=OnError.IGNORE, value_to_return_on_error=False)
def is_directory(path: PathLike) -> bool:
    return os_path.isdir(from_path_like(path))


@catch(default_on_error_behavior=OnError.IGNORE, value_to_return_on_error=False)
def is_link(path: PathLike) -> bool:
    """
    Return True if path refers to an existing directory entry that is a symbolic link.
    Always False if symbolic links are not supported by the Python runtime.
    """
    return False


@catch(default_on_error_behavior=OnError.IGNORE, value_to_return_on_error=False)
def is_mount(path: PathLike) -> bool:
    """
    Return True if pathname path is a mount point: a point in a file system where a different
    file system has been mounted.

    On POSIX, the function checks whether path’s parent, path/..,
    is on a different device than path, or whether path/.. and path point to the same i-node on the
    same device — this should detect mount points for all Unix and POSIX variants.
    It is not able to reliably detect bind mounts on the same filesystem.

    On Windows, a drive letter root and a share UNC are always mount points, and for any other path
    GetVolumePathName is called to see if it is different from the input path.
    """
    return os_path.ismount(from_path_like(path))


@catch(value_to_return_on_error=False)
def create_file(path: PathLike, should_not_exist: bool = False) -> bool:
    open(from_path_like(path), "x" if should_not_exist else "w").close()
    return True


def delete_file(path: PathLike, *, on_error: OnError = OnError.LOG) -> bool:
    try:
        os.remove(from_path_like(path))
        return True
    except IsADirectoryError as error:
        handle_error(error, on_error, message=f"Unable to delete {on_error} as it is a directory")
    except Exception as error:
        handle_error(error, on_error, message=f"Unable to delete file {on_error}")
    return False


@catch()
def rename(path: PathLike, new_name: PathLike) -> bool:
    os.rename(from_path_like(path), from_path_like(new_name))
    return True


@catch(value_to_return_on_error=False)
def copy_file(from_: PathLike, to_: PathLike) -> bool:
    shutil.copyfile(from_path_like(from_), from_path_like(to_))
    return True


@catch(value_to_return_on_error=False)
def move_file(from_: PathLike, to_: PathLike) -> bool:
    shutil.move(from_path_like(from_), from_path_like(to_))
    return True


@catch(value_to_return_on_error=False)
def copy_directory(from_: PathLike, to_: PathLike) -> bool:
    shutil.copytree(from_path_like(from_), from_path_like(to_))
    return True


@catch(value_to_return_on_error=False)
def move_directory(from_: PathLike, to_: PathLike) -> bool:
    shutil.move(from_path_like(from_), from_path_like(to_))
    return True


@catch(value_to_return_on_error=False)
def mkdir(path: PathLike, *, ignore_existing: bool = True) -> bool:
    os.makedirs(from_path_like(path), exist_ok=ignore_existing)
    return True


@catch(value_to_return_on_error=False)
def rmdir(path: PathLike, *, must_be_empty: bool = False) -> bool:
    if must_be_empty:
        os.rmdir(from_path_like(path))
    else:
        shutil.rmtree(from_path_like(path))
    return True


def remake_dir(path: PathLike) -> bool:
    return rmdir(path) and mkdir(path)


def get_next_available_file_name(
    path: PathLike,
    *,
    separator: str = "",
    start_integer: int = 0,
    max_limit: int = 1_000_000,
    step: int = 1,
) -> str:
    """
    If the file at *path* exists, adds an integer to the file name and increments until the created
    filename does not refer to an existing file.
    :param path: The file full path
    :param separator: Character(s) that separate file name and integer
    :param start_integer: Starts at this value
    :param max_limit: Specifies the maximum the integer can be
    :param step: The step to increment the integer
    :return: The new path
    :raises: OverflowError when reaching *max_limit*
    """
    file_name_only: str
    extension: str
    path_part: str

    path_part, file_name_only, extension = get_path_parts_and_extension(from_path_like(path))

    for i in range(start_integer, max_limit, step):
        path_candidate: str = join(path_part, f"{file_name_only}{separator}{i}.{extension}")
        if not is_file(path_candidate):
            return path_candidate

    raise OverflowError(f"Reached maximum limit of {max_limit} for file {path}")


@catch(value_to_return_on_error=False)
def make_symlink(source_path: PathLike, target_path: PathLike) -> bool:
    """
    Create a symbolic link pointing to src named dst.

    On Windows, a symlink represents either a file or a directory, and does
    not morph to the target dynamically. If the target is present, the type of
    the symlink will be created to match.
    """
    os.symlink(
        from_path_like(source_path),
        from_path_like(target_path),
        os_name() == "windows" and os_path.isdir(from_path_like(source_path)),
    )
    return True


@catch(value_to_return_on_error=False)
def make_hard_link(source_path: PathLike, target_path: PathLike) -> bool:
    os.link(from_path_like(source_path), from_path_like(target_path))
    return True


@catch(value_to_return_on_error=-1)
def get_file_size(file: PathLike) -> int:
    return os_path.getsize(from_path_like(file))


@catch()
def get_file_last_access_datetime(file: PathLike) -> datetime:
    return datetime.fromtimestamp(os_path.getatime(from_path_like(file)))


@catch()
def get_file_creation_datetime(file: PathLike) -> datetime:
    return datetime.fromtimestamp(os_path.getctime(from_path_like(file)))


@catch()
def get_file_last_modified_datetime(file: PathLike) -> datetime:
    return datetime.fromtimestamp(os_path.getmtime(from_path_like(file)))


@contextmanager
def open_read(
    file: str,
    buffering: int | BufferingEnum = BufferingEnum.DEFAULT,
    encoding: str = "utf8",
    newline: str = "\n",
    binary: bool = False,
) -> Generator[TextIO | BinaryIO, Any, None]:
    f: TextIO | BinaryIO = open(
        file,
        f'r{"b" if binary else ""}',
        buffering=coalesce(maybe_enum(buffering), buffering),
        encoding=encoding,
        newline=newline,
    )
    try:
        yield f
    finally:
        f.close()


@contextmanager
def open_write(
    file: str,
    buffering: int | BufferingEnum = BufferingEnum.DEFAULT,
    encoding: str = "utf8",
    newline: str = "\n",
    binary: bool = False,
) -> Generator[TextIO | BinaryIO, Any, None]:
    f: TextIO | BinaryIO = open(
        file,
        f'w{"b" if binary else ""}',
        buffering=coalesce(maybe_enum(buffering), buffering),
        encoding=encoding,
        newline=newline,
    )
    try:
        yield f
    finally:
        f.close()


@contextmanager
def open_append(
    file: str,
    buffering: int | BufferingEnum = BufferingEnum.DEFAULT,
    encoding: str = "utf8",
    newline: str = "\n",
    binary: bool = False,
) -> Generator[TextIO | BinaryIO, Any, None]:
    f: TextIO | BinaryIO = open(
        file,
        f'a{"b" if binary else ""}',
        buffering=coalesce(maybe_enum(buffering), buffering),
        encoding=encoding,
        newline=newline,
    )
    try:
        yield f
    finally:
        f.close()


@contextmanager
def open_random(
    file: str,
    starting_location: StartLocationsEnum = StartLocationsEnum.START_OF_FILE_NO_TRUNCATE,
    buffering: int | BufferingEnum = BufferingEnum.DEFAULT,
    encoding: str = "utf8",
    newline: str = "\n",
    binary: bool = False,
) -> Generator[TextIO | BinaryIO, Any, None]:
    f: TextIO | BinaryIO = open(
        file,
        f'{starting_location.value}{"b" if binary else ""}',
        buffering=coalesce(maybe_enum(buffering), buffering),
        encoding=encoding,
        newline=newline,
    )
    try:
        yield f
    finally:
        f.close()


def merge_files(
    *files: str,
    destination_path: str,
    ignore_non_existent_files: bool = False,
    block_size: int = 65_536,
    on_error: OnError = OnError.LOG,
    join_token: str = "",
) -> bool:
    try:
        with open_write(destination_path) as out_file:
            for file in files:
                try:
                    with open_read(file) as f:
                        shutil.copyfileobj(f, out_file, block_size)
                        if join_token:
                            f.write(join_token)
                except FileNotFoundError:
                    if not ignore_non_existent_files:
                        raise
        return True
    except Exception as error:
        handle_error(error, on_error)
        return False


def count_lines(file: str, on_error: OnError = OnError.LOG) -> int:
    count: int = 0
    try:
        with open_read(file) as f:
            for l in f:
                count += 1
    except Exception as error:
        handle_error(error, on_error)

    return count


def ungzip_to_text(
    archive_path: str,
    destination_path: str,
    block_size: int = 65_536,
    on_error: OnError = OnError.LOG,
) -> bool:
    try:
        with gzip.open(archive_path, "rb") as gz_file, open(destination_path, "wb") as out_file:
            shutil.copyfileobj(gz_file, out_file, block_size)
        return True
    except Exception as error:
        handle_error(error, on_error)
        return False
