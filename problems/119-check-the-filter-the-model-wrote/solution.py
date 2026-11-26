from datetime import date
import json
import math


def _coerce(value, field_type):
    if isinstance(value, bool):
        raise ValueError("bool is not allowed")

    if field_type in (int, "int", "integer"):
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            if math.isfinite(value) and value.is_integer():
                return int(value)
            raise ValueError("non-whole float")
        if isinstance(value, str):
            return int(value)
        raise ValueError("invalid int")

    if field_type in (float, "float", "number"):
        if isinstance(value, (int, float)):
            val = float(value)
            if not math.isfinite(val):
                raise ValueError("non-finite float")
            return val
        if isinstance(value, str):
            val = float(value)
            if not math.isfinite(val):
                raise ValueError("non-finite float")
            return val
        raise ValueError("invalid float")

    if field_type in (date, "date"):
        if isinstance(value, str):
            return date.fromisoformat(value)
        raise ValueError("invalid date")

    if field_type in (str, "str", "string"):
        if isinstance(value, str):
            return value.strip().lower()
        raise ValueError("invalid str")

    raise ValueError("unknown field type")


def self_query(question, write, docs, k=3):
    reply = write(SELF_QUERY_PROMPT.format(question=question))

    parsed = None
    if isinstance(reply, str):
        start = reply.find("{")
        end = reply.rfind("}")
        if start != -1 and end != -1 and start < end:
            try:
                obj = json.loads(reply[start : end + 1])
                if isinstance(obj, dict):
                    parsed = obj
            except json.JSONDecodeError:
                parsed = None

    if parsed is None:
        query = question
        raw_filter = []
    else:
        raw_query = parsed.get("query")
        if isinstance(raw_query, str) and raw_query.strip():
            query = raw_query.strip()
        else:
            query = question

        raw_filter = parsed.get("filter")
        if not isinstance(raw_filter, list):
            raw_filter = []

    clauses = []
    for clause in raw_filter:
        if not isinstance(clause, dict):
            continue
        field = clause.get("field")
        op = clause.get("op")
        if not isinstance(field, str) or not isinstance(op, str):
            continue
        if field not in SCHEMA:
            continue

        field_type = SCHEMA[field]
        if op not in ALLOWED_OPS.get(field_type, ()):
            continue
        if "value" not in clause:
            continue

        raw_val = clause["value"]
        try:
            if op == "in":
                if not isinstance(raw_val, list):
                    continue
                coerced_val = [_coerce(item, field_type) for item in raw_val]
            else:
                coerced_val = _coerce(raw_val, field_type)
        except (ValueError, TypeError):
            continue

        clauses.append((field, op, coerced_val))

    matched = []
    for idx, doc in enumerate(docs):
        if all(
            field in doc and OPS[op](doc[field], val)
            for field, op, val in clauses
        ):
            matched.append((idx, doc))

    matched.sort(key=lambda item: (-similarity(query, item[1]["text"]), item[0]))
    ids = [doc["id"] for _, doc in matched[:k]]

    return {
        "query": query,
        "filter": clauses,
        "ids": ids,
    }
