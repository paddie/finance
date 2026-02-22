#!/usr/bin/env python3
"""Split Spiir CSV files by AccountName.

Usage: python split_by_account.py *.csv
"""

import csv
import sys
from pathlib import Path


def split_file(src: Path):
    with open(src, encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh, delimiter=";")
        fieldnames = reader.fieldnames
        buckets: dict[str, list] = {}
        for row in reader:
            name = row["AccountName"].lower()
            buckets.setdefault(name, []).append(row)

    year = src.stem
    for name, rows in sorted(buckets.items()):
        safe = name.replace(" ", "_")
        dst = src.parent / f"{safe}_{year}.csv"
        with open(dst, "w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.DictWriter(
                fh, fieldnames=fieldnames, delimiter=";", quoting=csv.QUOTE_ALL
            )
            writer.writeheader()
            writer.writerows(rows)
        print(f"  {dst.name}: {len(rows)} rows")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <file.csv> [file2.csv ...]", file=sys.stderr)
        sys.exit(1)

    for arg in sys.argv[1:]:
        src = Path(arg)
        print(f"Splitting {src.name}...")
        split_file(src)


if __name__ == "__main__":
    main()
