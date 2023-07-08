import os
import re
from typing import Callable, TypeVar

from empire_commons.on_error import OnError, catch
from empire_commons.regex_util import RegexUtil

from efs.path import PathLike, from_path_like

__all__ = [
    "ConfigurableCallbacks",
    "PredefinedCallbacks",
    "scan_directory",
    "ScanDirectoryResult",
]


ScanDirectoryResult = TypeVar("ScanDirectoryResult")


class PredefinedCallbacks:
    @staticmethod
    def directories_only(entry_path: str, is_directory: bool, dir_entry: os.DirEntry, kwargs_dict: dict) -> ScanDirectoryResult:
        return entry_path if is_directory else None

    @staticmethod
    def files_only(entry_path: str, is_directory: bool, dir_entry: os.DirEntry, kwargs_dict: dict) -> ScanDirectoryResult:
        return entry_path if not is_directory else None

    @staticmethod
    def file_names_only(entry_path: str, is_directory: bool, dir_entry: os.DirEntry, kwargs_dict: dict) -> ScanDirectoryResult:
        return dir_entry.name if not is_directory else None


class ConfigurableCallbacks:
    @staticmethod
    def match_pattern(
        pattern: str,
    ) -> Callable[[str, bool, os.DirEntry, dict], ScanDirectoryResult]:
        compiled_pattern: re.Pattern = RegexUtil.get_compiled_re(pattern)

        def _match_pattern(
            entry_path: str,
            is_directory: bool,
            dir_entry: os.DirEntry,
            kwargs_dict: dict,
        ) -> ScanDirectoryResult:
            name: str = dir_entry.name
            if compiled_pattern.match(compiled_pattern):
                return entry_path

            return None

        return _match_pattern
    
    @staticmethod
    def file_extensions(
        *extensions: str
    ) -> Callable[[str, bool, os.DirEntry, dict], ScanDirectoryResult]:
        def _file_extensions(
            entry_path: str,
            is_directory: bool,
            dir_entry: os.DirEntry,
            kwargs_dict: dict,
        ) -> ScanDirectoryResult:
            for extension in extensions:
                if dir_entry.name.endswith(extension):
                    return entry_path

            return None

        return _file_extensions


@catch(default_on_error_behavior=OnError.LOG)
def scan_directory(
    path: PathLike,
    *,
    recursive: bool = False,
    on_entry_found_callback: Callable[[str, bool, os.DirEntry, dict], ScanDirectoryResult] = None,
    **on_entry_found_callback_kwargs,
) -> list[str]:
    if on_entry_found_callback is None:
        on_entry_found_callback = lambda w, x, y, z: w

    def _recursion(path_: str) -> list[ScanDirectoryResult]:
        results: list[ScanDirectoryResult] = []
        f: os.DirEntry
        for f in os.scandir(path_):
            if recursive and f.is_dir():
                results.extend(_recursion(f.path))

            result: ScanDirectoryResult = on_entry_found_callback(f.path, f.is_dir(), f, on_entry_found_callback_kwargs)
            if result is not None:
                results.append(result)

        return results

    return _recursion(from_path_like(path))
