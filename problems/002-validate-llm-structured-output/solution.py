import json


def validate_response(raw, schema):
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None

    if not isinstance(data, dict):
        return None

    cleaned = {}
    for field, expected_type in schema.items():
        if field not in data:
            return None
        val = data[field]
        if expected_type is int and isinstance(val, bool):
            return None
        if not isinstance(val, expected_type):
            return None
        cleaned[field] = val

    return cleaned
