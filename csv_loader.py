"""Reading CSV files into flight records and error messages."""

import csv
import os

from validator import to_record, validate_row


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process the CSV files in the order given.

    Return (records, errors):
      records - valid flight records, in input order
      errors  - one message per invalid row, in input order, formatted as
                "<file name>:<line number>: <ERROR_CODE> | <free text>"
                (base file name only, no timestamp or level, no newline)

    Also performs the DUPLICATE_FLIGHT check across all the files.
    Does not write any files and does not log anything itself.
    """
    records: list[dict] = []
    errors: list[str] = []
    seen: set[tuple[str, str]] = set()

    for path in paths:
        base_name = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            for line_no, raw_line in enumerate(f, start=1):
                if line_no == 1:
                    continue

                line_clean = raw_line.rstrip("\r\n")
                stripped_line = line_clean.strip()
                if not stripped_line or stripped_line.startswith("#"):
                    continue

                fields = next(csv.reader([line_clean]))
                error_code = validate_row(fields, airports)
                if error_code is not None:
                    errors.append(f"{base_name}:{line_no}: {error_code} | {line_clean}")
                    continue

                record = to_record(fields)
                key = (record["flight_id"], record["departure_datetime"])
                if key in seen:
                    errors.append(f"{base_name}:{line_no}: DUPLICATE_FLIGHT | {line_clean}")
                    continue

                seen.add(key)
                records.append(record)

    return records, errors