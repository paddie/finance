from datetime import datetime
import pathlib
from datetime import datetime, date
from typing import Optional
from beangulp import Importer
from beancount.core.data import Transaction, Account


class SpiirImporter(Importer):

    def name(self) -> str:
        return "spiir"

    def identify(self, filepath: str) -> bool:
        # files in spiir has the format:
        # ~/Documents/finance/spiir/<acccount>_<date>.csv
        file = pathlib.Path(filepath)
        filename = file.name
        if not filename.endswith(".csv"):
            return False

        if filename.count("_") != 1:
            return False

        # validate that the date part of the filename is a valid year
        account, date_str = filename.split("_")
        date_str = date_str.split(".")[0]
        try:
            datetime.strptime(date_str, "%Y")
        except ValueError:
            return False

        # check that csv header matches expected format
        header = '''"Id";"AccountId";"AccountName";"AccountType";"Date";"Description";"OriginalDescription";"MainCategoryId";"MainCategoryName";"CategoryId";"CategoryName";"CategoryType";"ExpenseType";"Amount";"Balance";"CounterEntryId";"Comment";"Tags";"Extraordinary";"SplitGroupId";"CustomDate";"Currency";"OriginalAmount";"OriginalCurrency"'''
        with open(filepath, "r") as f:
            first_line = f.readline().strip()
            if first_line != header:
                return False
        return True

    def account(self, filepath: str) -> Account:
        # files in spiir has the format:
        # ~/Documents/finance/spiir/<acccount>_<date>.csv
        # ignore the prefix, and focus on the filename
        # use a safe filepath splitter
        file = pathlib.Path(filepath)
        filename = file.name
        account_name = filename.split("_")[0]
        return f"Assets:Checking:{account_name.title()}"

    def date(self, filepath: str) -> Optional[date]:
        # files in spiir has the format:
        # ~/Documents/finance/spiir/<acccount>_<year>.csv
        # export the date as january first of the following year.
        file = pathlib.Path(filepath)
        filename = file.name
        date_str = filename.split("_")[1].split(".")[0]
        year = int(date_str)
        return date(year + 1, 1, 1)
