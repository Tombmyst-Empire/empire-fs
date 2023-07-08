from yaml import dump, load

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader, Dumper

from empire_commons.on_error import catch
from empire_commons.types_ import JsonType

from efs.io_ import OpenFileForAppend, OpenFileForRead, OpenFileForWrite


class YML_IO:
    @staticmethod
    @catch()
    def read_yml_from_file(file: str) -> JsonType:
        with OpenFileForRead(file) as f:
            return load(f, Loader=Loader)

    @staticmethod
    @catch()
    def write_to_yml_file(file: str, data: JsonType):
        with OpenFileForWrite(file) as f:
            dump(data, f)

    @staticmethod
    @catch()
    def append_to_yml_file(file: str, data: JsonType):
        with OpenFileForAppend(file) as f:
            dump(data, f)
