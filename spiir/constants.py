from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

PRIMARY_ACCOUNT = "Assets:DanskeBank:Primary"
FIXED_ACCOUNT = "Assets:DanskeBank:Fixed"
DAGLIGVARER_ACCOUNT = "Assets:DanskeBank:Dagligvarer"
SAVINGS_ACCOUNT = "Assets:DanskeBank:Opsparing"

ACCOUNT_MAP = {
    "primary": PRIMARY_ACCOUNT,
    "faste fællesudgifter": FIXED_ACCOUNT,
    "kærestekonto": DAGLIGVARER_ACCOUNT,
    "opsparing": SAVINGS_ACCOUNT,
}


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
