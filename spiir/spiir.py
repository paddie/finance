from datetime import datetime
import pathlib
from datetime import datetime, date
from typing import Optional
from typing import Iterator
from beangulp import Importer
from beancount.core import data 
import csv
import re
from dataclasses import dataclass
from decimal import Decimal

from . import constants
from . import rules

class SpiirImporter(Importer):

    def name(self) -> str:
        return "spiir"

    def identify(self, filepath: str) -> bool:
        # files in spiir has the format:
        # ~/Documents/finance/spiir/<acccount>_<date>.csv
        file = pathlib.Path(filepath)
        filename = file.name
        if not filename.endswith(".csv"):
            print(f"not a csv file: {filename}")
            return False

        # check that csv header matches expected format
        header = '"Id";"AccountId";"AccountName";"AccountType";"Date";"Description";"OriginalDescription";"MainCategoryId";"MainCategoryName";"CategoryId";"CategoryName";"CategoryType";"ExpenseType";"Amount";"Balance";"CounterEntryId";"Comment";"Tags";"Extraordinary";"SplitGroupId";"CustomDate";"Currency";"OriginalAmount";"OriginalCurrency"'
        with open(filepath, encoding="utf-8-sig") as f:
            first_line = f.readline().strip()
            if first_line != header:
                print(f"{filepath}: csv header does not match expected format: {first_line}")
                return False
        return True

    def account(self, filepath: str) -> data.Account:
        # files in spiir has the format:
        # ~/Documents/finance/spiir/<acccount>_<date>.csv
        # return the account name
        return "Assets:DanskeBank"

    def filename(self, filepath: str) -> data.Account:
        # files in spiir has the format:
        # ~/Documents/finance/spiir/<acccount>_<date>.csv
        # ignore the prefix, and focus on the filename
        # use a safe filepath splitter
        return "danskebank." + pathlib.basename(filepath)

    def date(self, filepath: str) -> Optional[date]:
        # files in spiir has the format:
        # ~/Documents/finance/spiir/<acccount>_<year>.csv
        # export the date as january first of the following year.
        file = pathlib.Path(filepath)
        filename = file.name
        date_str = filename.split(".")[0]
        year = int(date_str)
        return date(year)

    def extract(self, filepath: str, existing: data.Entries) -> data.Entries:
        entries = []
        filename = pathlib.Path(filepath).name
        # get row and index
        for index, row in enumerate[constants.SpiirRow](self._read_spiir_rows(filepath)):
            entries.append(self._row_to_transaction(index+1, row, filename))
        return entries

    def _row_to_transaction(self, index: int, row: constants.SpiirRow, filename: str) -> data.Transaction:
        """Convert a SpiirRow to a beancount Transaction."""
        asset_account = constants.ACCOUNT_MAP.get(
            row.account_name, "Assets:DanskeBank"
        )
        category_account = rules.classify_account(
            asset_account, row
        )

        tags = {"danskebank"}
        if row.tags:
            for t in row.tags.split(","):
                sanitized = _sanitize_tag(t)
                if sanitized:
                    tags.add(sanitized)
        
        # TODO: metadata can include linenumber to original file for easier debugging of classification rules, e.g.:
        meta = data.new_metadata(filename, index)
        meta["danskebank-id"] = row.id
        if row.counter_entry_id:
            meta["danskebank-counter-id"] = row.counter_entry_id
            tags.add("transfer")

        amount = data.Amount(row.amount.quantize(Decimal("0.01")), "DKK")
        inv_amount = data.Amount((-row.amount).quantize(Decimal("0.01")), "DKK")

        postings = [
            data.Posting(asset_account, amount, None, None, None, None),
            data.Posting(category_account, inv_amount, None, None, None, None),
        ]

        return data.Transaction(
            meta=meta,
            date=row.date,
            flag="*",
            payee=row.description,
            narration=row.category_name,
            tags=frozenset(tags),
            links=frozenset(),  
            postings=postings,
        )
    def _read_spiir_rows(self, filepath : str) -> Iterator[constants.SpiirRow]:
        """Read a CSV file and yield SpiirRow instances."""
        with open(filepath, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f, delimiter=";"):
                custom_date_str = row.get("CustomDate", "").strip()
                yield constants.SpiirRow(
                    id=row["Id"],
                    account_id=row["AccountId"].casefold(),
                    account_name=row["AccountName"].casefold(),
                    account_type=row["AccountType"].casefold(),
                    date=_parse_date(custom_date_str or row["Date"]),
                    description=row["Description"].strip().casefold(),
                    original_description=row["OriginalDescription"].casefold(),
                    main_category_id=row["MainCategoryId"].casefold(),
                    main_category_name=row["MainCategoryName"].casefold(),
                    category_id=row["CategoryId"],
                    category_name=row["CategoryName"].casefold(),
                    category_type=row["CategoryType"].casefold(),
                    expense_type=row["ExpenseType"].casefold(),
                    amount=_parse_decimal(row["Amount"]),
                    balance=_parse_decimal(row["Balance"]),
                    counter_entry_id=row["CounterEntryId"],
                    comment=row.get("Comment", "").casefold(),
                    tags=row.get("Tags", "").strip().casefold(),
                    extraordinary=row["Extraordinary"].casefold(),
                    split_group_id=row.get("SplitGroupId", ""),
                    custom_date=(
                        _parse_date(custom_date_str) if custom_date_str else None
                    ),
                    currency=row["Currency"],
                    original_amount=_parse_decimal(row["OriginalAmount"]),
                    original_currency=row["OriginalCurrency"],
                )


def _parse_date(s: str) -> date:
    """Parse DD-MM-YYYY to date."""
    return datetime.strptime(s, "%d-%m-%Y").date()


def _parse_decimal(s: str) -> Decimal:
    """Parse Danish number format (comma decimal, dot thousands) to Decimal."""
    s = s.strip()
    if not s:
        return Decimal("0.00")
    return Decimal(s.replace(".", "").replace(",", "."))


def _sanitize_tag(tag: str) -> str:
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
