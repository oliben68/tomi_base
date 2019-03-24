from collections.abc import MutableMapping, MutableSequence, Collection, Iterable

from morph import unflatten

DEFAULT_IDX_MARKER = "idx_"
DEFAULT_SEPARATOR = "."
MORPH_SEPARATOR = "."
DEFAULT_NULL_IDX = -1
EMPTY_DICT_PLACEHOLDER = "{empty map}"
EMPTY_ARRAY_PLACEHOLDER = "[empty list]"


def get_defaults(sep, idx_marker):
    return DEFAULT_SEPARATOR if sep is None else sep, DEFAULT_IDX_MARKER if idx_marker is None else idx_marker


def flatten(obj, key='', sep=None, idx_marker=None):
    if not isinstance(obj, Iterable) or isinstance(obj, (str, bytes)):
        return obj

    sep, idx_marker = get_defaults(sep, idx_marker)

    def to_dict(c):
        if isinstance(obj, MutableMapping):
            return c
        return {idx_marker + str(key): val for key, val in enumerate(c)}

    items = []
    if not isinstance(obj, Collection) or isinstance(obj, str):
        return {key: obj}

    for item in to_dict(obj).items():
        k = item[0]
        v = item[1]
        new_key = key + sep + k if key else k

        if isinstance(v, MutableMapping):
            if len(v) == 0:
                items.extend({new_key: EMPTY_DICT_PLACEHOLDER}.items())
            else:
                items.extend(flatten(v, key=new_key, sep=sep).items())
        elif isinstance(v, MutableSequence) or type(v) in (set, tuple):
            if len(v) == 0:
                items.extend({new_key: EMPTY_ARRAY_PLACEHOLDER}.items())
            else:
                new_value = {idx_marker + str(k): v for k, v in enumerate(v)}
                items.extend(flatten(new_value, key=new_key, sep=sep).items())
        else:
            items.append((new_key, v))

    return dict(items)


def dict_to_array(obj, idx_marker=None):
    try:
        iter(obj)
        if type(obj) == str:
            if obj == EMPTY_DICT_PLACEHOLDER:
                return {}
            elif obj == EMPTY_ARRAY_PLACEHOLDER:
                return []
            return obj
    except TypeError:
        return obj

    _, idx_marker = get_defaults(None, idx_marker)

    keys = list(obj.keys())

    is_list = all([key.startswith(idx_marker) for key in keys])
    if is_list:
        new_array = [None] * len(keys)
        for key in keys:
            new_array[int(key.replace(idx_marker, ""))] = dict_to_array(obj[key])
        return new_array

    for key in keys:
        obj[key] = dict_to_array(obj[key])
    return obj


def expand(obj, sep=None, idx_marker=None):
    sep, idx_marker = get_defaults(sep, idx_marker)

    if sep != MORPH_SEPARATOR:
        new_obj = {}
        for key in obj.keys():
            new_obj[key.replace(sep, MORPH_SEPARATOR)] = obj[key]
        obj = new_obj

    return dict_to_array(unflatten(obj))


def flatten_lists(lst):
    def iterable(v):
        return isinstance(v, Iterable) and not type(v) == str

    return [val for sub in [v for v in lst if iterable(v)] for val in sub] + [val for val in lst if not iterable(val)]
