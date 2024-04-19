import json


def validate_json(data: any) -> bool:
    try:
        return bool(json.loads(data))
    except:
        return False


SERIALIZERS = [
    {
        "validate": lambda data: data is None,
        "serialize": lambda data: (None, data),
    },
    {
        "validate": validate_json,
        "serialize": lambda data: ("application/json", data),
    },
    {
        "validate": lambda data: isinstance(data, dict),
        "serialize": lambda data: ("application/json", json.dumps(data)),
    },
    {
        "validate": lambda data: isinstance(data, list),
        "serialize": lambda data: ("application/json", json.dumps(data)),
    },
    {
        "validate": lambda data: hasattr(data, "__dict__"),
        "serialize": lambda data: ("application/json", json.dumps(data.__dict__)),
    },
    {
        "validate": lambda data: hasattr(data, "__anext__")
        or hasattr(data, "__next__"),
        "serialize": lambda data: ("application/octet-stream", data),
    },
]
