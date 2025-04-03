from typing import Union, Any


def json_path(path: list[Union[str, int]], value: Union[dict, list], default=None) -> Any:
    """Try fetching data from a "json path" """

    current: Any = value
    for key in path:
        if isinstance(current, dict) and isinstance(key, str):
            current = current.get(key, default)
        elif isinstance(current, list) and isinstance(key, int):
            if 0 <= key < len(current):
                current = current[key]
            else:
                return default
        else:
            return None
    return current
