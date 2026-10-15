"""Clean a messy CSV file: tidy headers, trim cells, drop empty and duplicate rows.

Usage:
    python csv_cleaner.py messy.csv                 # writes messy_clean.csv
    python csv_cleaner.py messy.csv -o result.csv   # choose the output name
    python csv_cleaner.py messy.csv --delimiter ";" # semicolon-separated input
"""
import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CleanStats:
    rows_in: int = 0
    rows_out: int = 0
    empty_removed: int = 0
    duplicates_removed: int = 0


def normalize_header(name: str) -> str:
    """' First  Name ' -> 'first_name'"""
    return re.sub(r"\s+", "_", name.strip().lower())


def clean_cell(value: str) -> str:
    """Trim the ends and collapse repeated inner whitespace into one space."""
    return re.sub(r"\s+", " ", value).strip()


def clean_rows(rows: list[list[str]]) -> tuple[list[list[str]], CleanStats]:
    """Clean a table whose first row is the header. Returns (new_rows, stats)."""
    if not rows:
        return [], CleanStats()

    header = [normalize_header(name) for name in rows[0]]
    stats = CleanStats(rows_in=len(rows) - 1)
    cleaned = [header]
    seen: set[tuple[str, ...]] = set()

    for line_number, row in enumerate(rows[1:], start=2):
        if len(row) > len(header):
            raise ValueError(
                f"line {line_number} has {len(row)} columns but the header has {len(header)}"
            )
        cells = [clean_cell(cell) for cell in row]
        cells += [""] * (len(header) - len(cells))  # pad short rows

        if not any(cells):
            stats.empty_removed += 1
            continue

        key = tuple(cells)
        if key in seen:
            stats.duplicates_removed += 1
            continue

        seen.add(key)
        cleaned.append(cells)

    stats.rows_out = len(cleaned) - 1
    return cleaned, stats


def clean_file(input_path: Path, output_path: Path, delimiter: str = ",") -> CleanStats:
    # utf-8-sig removes the invisible BOM character that Excel adds to CSV files
    with input_path.open(newline="", encoding="utf-8-sig") as source:
        rows = list(csv.reader(source, delimiter=delimiter))

    cleaned, stats = clean_rows(rows)

    with output_path.open("w", newline="", encoding="utf-8") as target:
        csv.writer(target, delimiter=delimiter).writerows(cleaned)

    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Clean a messy CSV file.")
    parser.add_argument("input", type=Path, help="CSV file to clean")
    parser.add_argument("-o", "--output", type=Path, help="output file (default: <input>_clean.csv)")
    parser.add_argument("--delimiter", default=",", help="column separator (default: ,)")
    args = parser.parse_args(argv)

    if not args.input.is_file():
        print(f"error: file not found: {args.input}")
        return 1

    output = args.output or args.input.with_name(f"{args.input.stem}_clean.csv")
    try:
        stats = clean_file(args.input, output, args.delimiter)
    except ValueError as error:
        print(f"error: {error}")
        return 1

    print(f"Rows read:          {stats.rows_in}")
    print(f"Empty rows removed: {stats.empty_removed}")
    print(f"Duplicates removed: {stats.duplicates_removed}")
    print(f"Rows written:       {stats.rows_out}")
    print(f"Saved to:           {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
