#!/usr/bin/env python3
"""Import Spiir CSV exports into beancount .bean files."""

import csv
import re
from typing import Iterator, Optional
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from beancount.core.amount import Amount
from beancount.core.data import Open, Posting, Transaction, new_metadata
from beancount.parser.printer import format_entry

import constants
import rules

BASE_DIR = Path(__file__).parent
SPIIR_DIR = BASE_DIR / "spiir"
MAIN_BEAN = BASE_DIR / "main.bean"

# --- Account mappings ---


@dataclass(frozen=True)
class SpiirRow:
    id: str
    account_id: str
    account_name: str
    account_type: str
    date: date
    description: str
    original_description: str
    main_category_id: str
    main_category_name: str
    category_id: str
    category_name: str
    category_type: str
    expense_type: str
    amount: Decimal
    balance: Decimal
    counter_entry_id: str
    comment: str
    tags: str
    extraordinary: str
    split_group_id: str
    custom_date: Optional[date]
    currency: str
    original_amount: Decimal
    original_currency: str


def _parse_date(s: str) -> date:
    """Parse DD-MM-YYYY to date."""
    return datetime.strptime(s, "%d-%m-%Y").date()


def _parse_decimal(s: str) -> Decimal:
    """Parse Danish number format (comma decimal, dot thousands) to Decimal."""
    s = s.strip()
    if not s:
        return Decimal("0.00")
    return Decimal(s.replace(".", "").replace(",", "."))


def sanitize_tag(tag: str) -> str:
    """Convert a tag string to a valid beancount tag (ASCII alphanumeric, hyphens, underscores)."""
    tag = tag.strip()
    for src, dst in [
        ("æ", "ae"),
        ("ø", "oe"),
        ("å", "aa"),
        ("Æ", "Ae"),
        ("Ø", "Oe"),
        ("Å", "Aa"),
    ]:
        tag = tag.replace(src, dst)
    tag = re.sub(r"[^a-zA-Z0-9_-]", "-", tag)
    tag = re.sub(r"-+", "-", tag).strip("-")
    return tag


# yield SpiirRow instances from all CSV files in SPIIR_DIR, sorted by filename
def read_spiir_rows() -> Iterator[SpiirRow]:
    """Read all CSV files and yield SpiirRow instances."""
    for csv_file in sorted(SPIIR_DIR.glob("*.csv")):
        with open(csv_file, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                custom_date_str = row.get("CustomDate", "").strip()
                yield SpiirRow(
                    id=row["Id"],
                    account_id=row["AccountId"],
                    account_name=row["AccountName"],
                    account_type=row["AccountType"],
                    date=_parse_date(custom_date_str or row["Date"]),
                    description=row["Description"].strip(),
                    original_description=row["OriginalDescription"],
                    main_category_id=row["MainCategoryId"],
                    main_category_name=row["MainCategoryName"],
                    category_id=row["CategoryId"],
                    category_name=row["CategoryName"],
                    category_type=row["CategoryType"],
                    expense_type=row["ExpenseType"],
                    amount=_parse_decimal(row["Amount"]),
                    balance=_parse_decimal(row["Balance"]),
                    counter_entry_id=row["CounterEntryId"],
                    comment=row.get("Comment", ""),
                    tags=row.get("Tags", "").strip(),
                    extraordinary=row["Extraordinary"],
                    split_group_id=row.get("SplitGroupId", ""),
                    custom_date=(
                        _parse_date(custom_date_str) if custom_date_str else None
                    ),
                    currency=row["Currency"],
                    original_amount=_parse_decimal(row["OriginalAmount"]),
                    original_currency=row["OriginalCurrency"],
                )


import rules


def spiir_row_to_transaction(row: SpiirRow) -> Transaction:
    """Convert a SpiirRow to a beancount Transaction."""
    asset_account = constants.ACCOUNT_MAP.get(
        row.account_name, f"Assets:Checking:Unknown"
    )
    category_account = rules.classify_account(
        asset_account, row.description, row.category_name
    )

    tags = {"spiir"}
    if row.tags:
        for t in row.tags.split(","):
            sanitized = sanitize_tag(t)
            if sanitized:
                tags.add(sanitized)

    # TODO: metadata can include linenumber to original file for easier debugging of classification rules, e.g.:
    meta = new_metadata("<import>", 0)
    meta["spiir-id"] = row.id

    amount = Amount(row.amount.quantize(Decimal("0.01")), "DKK")
    inv_amount = Amount((-row.amount).quantize(Decimal("0.01")), "DKK")

    postings = [
        Posting(asset_account, amount, None, None, None, None),
        Posting(category_account, inv_amount, None, None, None, None),
    ]

    return Transaction(
        meta=meta,
        date=row.date,
        flag="*",
        payee=row.description,
        narration=row.category_name,
        tags=frozenset(tags),
        links=frozenset(),
        postings=postings,
    )


def make_opening_balance(account: str, amount: Decimal, d: date) -> Transaction:
    """Build an opening balance Transaction."""
    meta = new_metadata("<import>", 0)
    qty = amount.quantize(Decimal("0.01"))
    postings = [
        Posting(account, Amount(qty, "DKK"), None, None, None, None),
        Posting("Equity:Opening-Balances", Amount(-qty, "DKK"), None, None, None, None),
    ]
    return Transaction(
        meta=meta,
        date=d,
        flag="*",
        payee="Opening Balance",
        narration="",
        tags=frozenset({"spiir"}),
        links=frozenset(),
        postings=postings,
    )


def make_open_directive(account: str, d: date) -> Open:
    """Build an Open directive."""
    return Open(
        meta=new_metadata("<import>", 0),
        date=d,
        account=account,
        currencies=["DKK"],
        booking=None,
    )


def compute_opening_balances(rows: list[SpiirRow]) -> list[tuple[str, Decimal, date]]:
    """Compute opening balance for each asset account from the first transaction.

    Returns list of (account, opening_amount, date) tuples.
    """
    first_by_account: dict[str, SpiirRow] = {}
    for row in rows:
        acct = constants.ACCOUNT_MAP.get(
            row.account_name, f"Assets:Checking:{row.account_name}"
        )
        if acct not in first_by_account or row.date < first_by_account[acct].date:
            first_by_account[acct] = row

    result = []
    for acct, row in sorted(first_by_account.items()):
        opening = row.balance - row.amount
        result.append((acct, opening, row.date))
    return result


def write_year_files(
    rows: list[SpiirRow], opening_balances: list[tuple[str, Decimal, date]]
):
    """Write per-year .bean files."""
    # Build transactions
    txn_by_year: dict[int, list[Transaction]] = {}
    for row in rows:
        txn = spiir_row_to_transaction(row)
        txn_by_year.setdefault(row.date.year, []).append(txn)

    # Build opening balance transactions grouped by year
    ob_by_year: dict[int, list[Transaction]] = {}
    for acct, amount, d in opening_balances:
        ob_txn = make_opening_balance(acct, amount, d)
        ob_by_year.setdefault(d.year, []).append(ob_txn)

    all_years = sorted(set(list(txn_by_year.keys()) + list(ob_by_year.keys())))

    for year in all_years:
        path = BASE_DIR / f"{year}.bean"
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"; Spiir import for {year}\n")
            f.write(f"; Generated by import_spiir.py\n\n")

            for ob in sorted(ob_by_year.get(year, []), key=lambda t: t.date):
                f.write(format_entry(ob))
                f.write("\n")

            year_txns = sorted(
                txn_by_year.get(year, []),
                key=lambda t: (t.date, t.meta.get("spiir-id", "")),
            )
            for txn in year_txns:
                f.write(format_entry(txn))
                f.write("\n")

        print(
            f"  Wrote {path.name}: {len(ob_by_year.get(year, []))} opening balances, {len(txn_by_year.get(year, []))} transactions"
        )

    return all_years


def collect_accounts(
    rows: list[SpiirRow], opening_balances: list[tuple[str, Decimal, date]]
):
    """Collect all accounts with their earliest date."""
    accounts: dict[str, date] = {}

    def track(account: str, d: date):
        if account not in accounts or d < accounts[account]:
            accounts[account] = d

    for row in rows:
        asset_acct = constants.ACCOUNT_MAP.get(
            row.account_name, f"Assets:Checking:{row.account_name}"
        )
        cat_acct = rules.CATEGORY_MAP.get(row.category_name, "Expenses:Other")
        track(asset_acct, row.date)
        track(cat_acct, row.date)

    for acct, _, d in opening_balances:
        track(acct, d)
        track("Equity:Opening-Balances", d)

    return accounts


def update_main_bean(all_years, accounts: dict[str, date]):
    """Update main.bean with includes and open directives."""
    lines = []

    lines.append('option "operating_currency" "DKK"')
    lines.append('option "booking_method" "FIFO"')
    lines.append("")

    lines.append("; --- Spiir imports ---")
    for year in sorted(all_years):
        lines.append(f'include "{year}.bean"')
    lines.append("")

    lines.append("; --- Spiir accounts ---")
    for account, earliest_date in sorted(accounts.items()):
        directive = make_open_directive(account, earliest_date)
        lines.append(format_entry(directive).rstrip())
    lines.append("")

    MAIN_BEAN.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Updated {MAIN_BEAN.name}")


def main():
    print("Reading Spiir CSVs...")
    rows = list(read_spiir_rows())
    print(f"  Found {len(rows)} transactions")

    print("Computing opening balances...")
    opening_balances = compute_opening_balances(rows)
    for acct, amount, d in opening_balances:
        print(f"  {acct}: {amount.quantize(Decimal('0.01'))} DKK on {d}")

    print("Writing year files...")
    all_years = write_year_files(rows, opening_balances)

    print("Collecting accounts...")
    accounts = collect_accounts(rows, opening_balances)
    print(f"  Found {len(accounts)} unique accounts")

    print("Updating main.bean...")
    update_main_bean(all_years, accounts)

    print("Done!")


if __name__ == "__main__":
    main()
