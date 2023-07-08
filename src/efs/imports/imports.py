import importlib.resources
import logging
from importlib import import_module, reload
from importlib import util as ImportUtil  # noqa
from os.path import sep
from types import ModuleType
from typing import *

from efs.path import expand_relative_path, get_file_extension


class Import:
    @staticmethod
    def from_(module_path: str) -> Union[ModuleType, None]:
        if not module_path:
            return None

        if sep in module_path:
            result: Union[ModuleType, None] = Import._dyn_import_file_path(module_path)
        else:
            result: Union[ModuleType, None] = Import._dyn_import_python_path(module_path)

        return result

    @staticmethod
    def reload_from_path(module_path: str) -> Optional[ModuleType]:
        module: ModuleType = Import.from_(module_path)
        if module:
            reload(module)
        else:
            logging.warning(f"Module {module_path} not found")

        return module

    @staticmethod
    def list_modules_in_package(package_path: str) -> list[str]:
        return [f"{package_path}.{module.replace('.py', '')}" for module in importlib.resources.contents(package_path) if not module.startswith("__")]

    @staticmethod
    def _dyn_import_python_path(module_path: str) -> Optional[ModuleType]:
        try:
            mod: ModuleType = import_module(module_path)
            return mod
        except ImportError:
            logging.exception(f"Cannot import module %s", module_path)
            return None

    @staticmethod
    def _dyn_import_file_path(module_path: str) -> Optional[ModuleType]:
        try:
            spec = ImportUtil.spec_from_file_location(
                get_file_extension(expand_relative_path(module_path)),
                expand_relative_path(module_path),
            )
            module_from_spec = ImportUtil.module_from_spec(spec)
            spec.loader.exec_module(module_from_spec)  # noqa
            return module_from_spec
        except ImportError:
            logging.exception(f"Cannot import module %s,", module_path)
            return None
