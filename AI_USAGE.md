# AI Usage Disclosure

## Tools used

- ChatGPT

## Conversation links

- Link 1: https://chatgpt.com/share/6b040aae-21b8-83ed-b33c-852247e39a62

## What I used them for

- Strict ASCII only validation for flight IDs, airport codes, zero padded datetimes, and finite positive pricess
- Structuring multi file UTF8 CSV loading with accurate 1-based physical line numbers and cross file duplicate detection
- Query validation (handling boolean vs. number checks, `order` requiring `sort_by`, and invalid query responses) and stable sorting
- Setting up `argparse` mutually exclusive groups, custom exit codes, and `logging.FileHandler` cleanup in `try/finally`

## Which parts of the code were AI generated or substantially AI assisted

| File | Function or part | How (generated / modified / explained) |
| --- | --- | --- |
| `validator.py` | `load_airports`, `validate_row`, `to_record`, `parse_exact_datetime` | Explained and generated |
| `csv_loader.py` | `parse_files` | Explained and generated |
| `query.py` | `run_query`, `run_queries`, validation and filtering helpers | Explained and generated |
| `flight_parser.py` | `main`, `_build_parser`, CLI error handling and logging setup | Explained and generated |

## Key prompts

1. Asked how to strictly validate flight CSV fields in Python 3.13 (ASCII-only regexes, exact `YYYY-MM-DD HH:MM` datetime parsing, finite positive float price) and structure `validator.py`
2. Asked how to read multiple UTF-8 CSV files with `\n` and `\r\n` endings while tracking 1-based physical line numbers and detecting duplicates across files in `csv_loader.py`
3. Asked how to validate query dicts (rejecting booleans as numbers, enforcing `order` with `sort_by`) and implement stable sorting/filtering in `query.py`
4. Asked how to configure `argparse` exit codes without `sys.exit()` inside `main()` and properly remove/close `logging.FileHandler` in `flight_parser.py`

## What I changed or verified myself

I integrated the suggested logic into the four starter modules, adjusted the function signatures and return formats to strictly match the specification, and configured the student constants in `flight_parser.py`. I also tested edge cases (such as CRLF line endings, cross-file duplicates, invalid query types, and repeated `main()` calls for logger cleanup) and verified that all public tests pass using `python tests/run_public_tests.py`