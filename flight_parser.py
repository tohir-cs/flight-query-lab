"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""

import argparse
from datetime import datetime
import json
import logging
import os
import sys

from csv_loader import parse_files
from query import run_queries
from validator import load_airports

STUDENT_ID = "251ADB079"
FIRST_NAME = "Tokhirbek"
LAST_NAME = "Akramov"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flight_parser.py",
        description="Validate flight schedule CSVs, build a JSON database, and run queries.",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i", dest="input_file", metavar="FILE", help="Parse a single CSV file.")
    source.add_argument("-d", dest="input_dir", metavar="FOLDER", help="Parse all .csv files in a folder.")
    source.add_argument("-j", dest="json_db", metavar="FILE", help="Load an existing JSON database.")

    parser.add_argument("-a", dest="airports", metavar="FILE", help="Airport list file (required with -i or -d).")
    parser.add_argument("-o", dest="output_db", metavar="FILE", help="Output JSON database path (default: db.json).")
    parser.add_argument("-q", dest="query_file", metavar="FILE", help="JSON file containing queries.")
    parser.add_argument("-r", dest="response_dir", metavar="FOLDER", default=".", help="Folder for the query response file.")
    return parser


def _print_error(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
        if (args.input_file or args.input_dir) and not args.airports:
            parser.error("-a is required when using -i or -d")
        if args.json_db and args.output_db is not None:
            parser.error("-o cannot be used with -j")
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1

    logger = logging.getLogger("flight_parser")
    handler: logging.FileHandler | None = None

    try:
        if args.json_db:
            with open(args.json_db, "r", encoding="utf-8") as f:
                db = json.load(f)
            if not isinstance(db, list) or not all(isinstance(item, dict) for item in db):
                _print_error("JSON database must be an array of objects.")
                return 1
        else:
            if args.input_file:
                if not os.path.isfile(args.input_file):
                    _print_error(f"CSV file not found: {args.input_file}")
                    return 1
                csv_paths = [args.input_file]
            else:
                if not os.path.isdir(args.input_dir):
                    _print_error(f"Folder not found: {args.input_dir}")
                    return 1
                csv_names = sorted(
                    name
                    for name in os.listdir(args.input_dir)
                    if name.endswith(".csv")
                    and os.path.isfile(os.path.join(args.input_dir, name))
                )
                if not csv_names:
                    _print_error(f"No .csv files found in folder: {args.input_dir}")
                    return 1
                csv_paths = [os.path.join(args.input_dir, name) for name in csv_names]

            airports = load_airports(args.airports)

            output_path = args.output_db if args.output_db is not None else "db.json"
            output_dir = os.path.dirname(output_path) or "."
            log_path = os.path.join(output_dir, "errors.log")

            logger.setLevel(logging.INFO)
            handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            logger.addHandler(handler)

            db, errors = parse_files(csv_paths, airports)
            for err in errors:
                logger.warning(err)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2)

        if args.query_file:
            with open(args.query_file, "r", encoding="utf-8") as f:
                queries_data = json.load(f)
            is_valid_shape = isinstance(queries_data, dict) or (
                isinstance(queries_data, list)
                and all(isinstance(item, dict) for item in queries_data)
            )
            if not is_valid_shape:
                _print_error("Query file must contain a JSON object or an array of objects.")
                return 1

            responses = run_queries(db, queries_data)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            response_name = (
                f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{timestamp}.json"
            )
            response_path = os.path.join(args.response_dir, response_name)
            with open(response_path, "w", encoding="utf-8") as f:
                json.dump(responses, f, indent=2)

        return 0
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        _print_error(str(exc))
        return 1
    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()


if __name__ == "__main__":
    sys.exit(main())