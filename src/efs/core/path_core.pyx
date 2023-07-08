import os
import os.path as os_path

IF UNAME_SYSNAME == "Windows":
    DEF PATH_SEPARATOR = "\\"
ELSE:
    DEF PATH_SEPARATOR = "/"


_cache = {}


def join(*args):
    cdef str result = PATH_SEPARATOR.join(filter(None, args)) or None
    return result


cpdef list split(str path):
    if not path:
        return None

    cdef str key = 'split_' + path
    if key in _cache:
        return _cache[key]

    cdef list result
    result = path.split(PATH_SEPARATOR)
    _cache[key] = result

    return result


cpdef bint is_absolute(str path):
    try:
        return os_path.isabs(path)
    except TypeError:
        return False


cpdef bint is_unix_like(str path):
    try:
        return '/' in path
    except TypeError:
        return False


cpdef bint is_windows_like(str path):
    try:
        return '\\' in path
    except TypeError:
        return False


cpdef str convert_path_to_windows(str path):
    try:
        return path.replace('/', '\\') or None
    except AttributeError:
        return None


cpdef str convert_path_to_unix(str path):
    try:
        return path.replace('\\', '/') or None
    except AttributeError:
        return None


cpdef str get_file_path(str path):
    if not path:
        return None
    elif PATH_SEPARATOR not in path:
        return None

    cdef result = join(*split(path)[:-1])
    if not result:
        return path

    return result


cpdef str get_file_path_absolute(str path):
    if not path:
        return None

    return os_path.dirname(os_path.realpath(path))


cpdef str get_file_extension(str path):
    if not path:
        return None

    cdef str file_name = get_file_name_with_extension(path)

    while file_name.startswith('.'):
        file_name = file_name[1:]

    if '.' not in file_name:
        return None

    return file_name.split('.', maxsplit=1)[1]


cpdef str get_file_name_with_extension(str path):
    if not path:
        return None

    cdef str result
    result = path.split(PATH_SEPARATOR)[-1]
    return result


cpdef str get_file_name_no_extension(str path):
    if not path:
        return None

    cdef result = path.split(PATH_SEPARATOR)[-1]
    cdef str prefixes = ''

    while result.startswith('.'):
        result = result[1:]
        prefixes += '.'

    return prefixes + result.split('.')[0]


cpdef get_path_parts_and_extension(str path):
    cdef result = (
        get_file_path(path),
        get_file_name_no_extension(path),
        get_file_extension(path)
    )
    return result


cpdef get_path_parts_no_extension(str path):
    cdef result = (
        get_file_path(path),
        get_file_name_no_extension(path)
    )
    return result


cpdef str remove_file_name_from_path_if_is_file(str path):
    if not path:
        return None

    if not os_path.isfile(path):
        return path

    cdef result = PATH_SEPARATOR.join(split(path)[:-1])
    return result or None


cpdef str expand_relative_path(str path):
    if not path:
        return None

    return os_path.abspath(path)


cpdef str get_user_directory():
    return os_path.expanduser('~')


cpdef str get_temp_directory():
    import tempfile
    return tempfile.gettempdir()


cpdef str get_current_working_directory():
    return os.getcwd()


cpdef void set_current_working_directory(str path):
    os.chdir(path)


cpdef str remove_extension(str path):
    if not path:
        return None

    cdef extension = get_file_extension(path)
    if not extension:
        return path

    cdef result = path[:-(len(extension) + 1)]
    return result


cpdef str get_parent(str path):
    if not path:
        return path

    if PATH_SEPARATOR not in path:
        return path

    cdef result = PATH_SEPARATOR.join(split(path)[:-1])
    return result


cpdef str find_parent_sibling_from_path(str path, str name):
    if not path or not name:
        return None

    cdef joint_path_name = join(path, name)
    if os_path.isdir(joint_path_name) or os_path.isfile(joint_path_name):
        return joint_path_name

    cdef current_path = path
    cdef parent = get_parent(path)

    while current_path != parent:
        joint_path_name = join(current_path, name)
        if os_path.isdir(joint_path_name) or os_path.isfile(joint_path_name):
            return joint_path_name

        current_path = parent
        parent = get_parent(current_path)

    return None

cpdef str strip_path_up_to_node_name(str path, str node_name, bint inclusive = False):
    if not path or not node_name:
        return None

    cdef list cleaned = []

    for node in split(path):
        if node == node_name:
            if inclusive:
                cleaned.append(node)
            break
        else:
            cleaned.append(node)

    cdef joined = join(*cleaned)
    return joined


cpdef str strip_path_up_to_node_name_reversed(str path, str node_name, bint inclusive = False):
    if not path or not node_name:
        return None

    cdef list cleaned = []

    for node in reversed(split(path)):
        if node == node_name:
            if inclusive:
                cleaned.insert(0, node)
            break
        else:
            cleaned.insert(0, node)

    cdef joined = join(*cleaned)
    return joined


cpdef str replace_extension(str path, str with_):
    if not path or with_ is None:
        return None

    cdef str extension = get_file_extension(path)
    if not extension:
        return path

    cdef str replaced = path[:-len(extension)] + with_
    return replaced


cpdef str get_node_at(str path, unsigned int index):
    cdef list split_path = split(path)
    return split_path[index]

cpdef str set_node_at(str path, unsigned int index, str new_node):
    cdef list split_path = split(path)
    split_path[index] = new_node
    return join(*split_path)
