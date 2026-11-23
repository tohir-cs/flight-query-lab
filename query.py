"""Running queries against the flight database."""

import math

from validator import parse_exact_datetime

RECORD_KEYS = {
    "flight_id",
    "origin",
    "destination",
    "departure_datetime",
    "arrival_datetime",
    "price",
}

ALLOWED_QUERY_KEYS = RECORD_KEYS | {"min_price", "sort_by", "order", "limit"}


def _is_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _is_valid_query(query: object) -> bool:
    if not isinstance(query, dict):
        return False

    if any(key not in ALLOWED_QUERY_KEYS for key in query):
        return False

    if "order" in query and "sort_by" not in query:
        return False

    for key, value in query.items():
        if key in ("flight_id", "origin", "destination"):
            if not isinstance(value, str):
                return False
        elif key in ("departure_datetime", "arrival_datetime"):
            if not isinstance(value, str) or parse_exact_datetime(value) is None:
                return False
        elif key in ("price", "min_price"):
            if not _is_number(value):
                return False
        elif key == "sort_by":
            if not isinstance(value, str) or value not in RECORD_KEYS:
                return False
        elif key == "order":
            if value not in ("asc", "desc"):
                return False
        elif key == "limit":
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                return False

    return True


def _matches_query(record: dict, query: dict) -> bool:
    if "flight_id" in query and record["flight_id"] != query["flight_id"]:
        return False
    if "origin" in query and record["origin"] != query["origin"]:
        return False
    if "destination" in query and record["destination"] != query["destination"]:
        return False
    if "departure_datetime" in query and record["departure_datetime"] < query["departure_datetime"]:
        return False
    if "arrival_datetime" in query and record["arrival_datetime"] > query["arrival_datetime"]:
        return False
    if "price" in query and record["price"] > query["price"]:
        return False
    if "min_price" in query and record["price"] < query["min_price"]:
        return False
    return True


def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """
    if not _is_valid_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    matches = [record for record in db if _matches_query(record, query)]

    if "sort_by" in query:
        sort_key = query["sort_by"]
        reverse = query.get("order", "asc") == "desc"
        matches = sorted(matches, key=lambda rec: rec[sort_key], reverse=reverse)

    if "limit" in query:
        matches = matches[: query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    if isinstance(queries, dict):
        return [run_query(db, queries)]
    return [run_query(db, q) for q in queries]