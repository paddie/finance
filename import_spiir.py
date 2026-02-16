#!/usr/bin/env python3
"""Import Spiir CSV exports into beancount .bean files."""

import csv
import re
from datetime import date, datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
SPIIR_DIR = BASE_DIR / "spiir"
MAIN_BEAN = BASE_DIR / "main.bean"

# --- Account mappings ---

ACCOUNT_MAP = {
    "Primary": "Assets:Checking:Primary",
    "Faste Fællesudgifter": "Assets:Checking:Fixed",
    "Kærestekonto": "Assets:Checking:Dagligvarer",
    "Opsparing": "Assets:Checking:Opsparing",
}

CATEGORY_MAP = {
    # Husholdning
    ("Husholdning", "Dagligvarer"): "Expenses:Food:Groceries",
    ("Husholdning", "Kantine- & frokostordning"): "Expenses:Food:Canteen",
    ("Husholdning", "Kiosk, bager & specialbutikker"): "Expenses:Food:Kiosk",
    # Transport
    ("Transport", "Bilforsikring & autohjælp"): "Expenses:Car:Insurance",
    ("Transport", "Brændstof"): "Expenses:Car:Gas",
    ("Transport", "Parkering"): "Expenses:Car:Parking",
    ("Transport", "Bus, tog, færge o.l."): "Expenses:Transport:Public",
    ("Transport", "Taxi"): "Expenses:Transport:Taxi",
    ("Transport", "Ejerafgift/grøn afgift"): "Expenses:Car:Tax",
    ("Transport", "Værksted & reservedele"): "Expenses:Car:Service",
    ("Transport", "Anden transport"): "Expenses:Transport:Other",
    # Bolig
    ("Bolig", "Boliglån/husleje"): "Expenses:House:Mortgage",
    ("Bolig", "El, vand, varme & renovation"): "Expenses:House:Heating",
    ("Bolig", "Ombygning & vedligehold"): "Expenses:House:Renovation",
    ("Bolig", "Husforsikring"): "Expenses:House:Insurance",
    ("Bolig", "Ejendomsskat"): "Expenses:House:Tax",
    ("Bolig", "Ejerforening"): "Expenses:House:Association",
    ("Bolig", "Have & planter"): "Expenses:House:Garden",
    ("Bolig", "Alarmsystem"): "Expenses:House:Alarm",
    ("Bolig", "Andre boligudgifter"): "Expenses:House:Other",
    ("Bolig", "Indbo- & familieforsikring"): "Expenses:House:Contents-Insurance",
    # Privatforbrug
    ("Privatforbrug", "Tøj, sko & accessories"): "Expenses:Shopping:Clothing",
    ("Privatforbrug", "Elektronik & computerudstyr"): "Expenses:Shopping:Electronics",
    ("Privatforbrug", "Møbler & boligudstyr"): "Expenses:Shopping:Furniture",
    ("Privatforbrug", "Bar, cafe & restaurant"): "Expenses:Food:Restaurant",
    ("Privatforbrug", "Fastfood & takeaway"): "Expenses:Food:Takeaway",
    ("Privatforbrug", "Biograf, koncerter & forlystelser"): "Expenses:Entertainment:Events",
    ("Privatforbrug", "Film, musik & læsestof"): "Expenses:Entertainment:Media",
    ("Privatforbrug", "Sport & fritid"): "Expenses:Entertainment:Sports",
    ("Privatforbrug", "Hobby & sportsudstyr"): "Expenses:Shopping:Sports",
    ("Privatforbrug", "Frisør & personlig pleje"): "Expenses:Shopping:Personal-Care",
    ("Privatforbrug", "Gaver & velgørenhed"): "Expenses:Gifts",
    ("Privatforbrug", "Kontanthævning & check"): "Expenses:Cash",
    ("Privatforbrug", "Online services & software"): "Expenses:Subscriptions:Software",
    ("Privatforbrug", "Serviceydelser & rådgivning"): "Expenses:Services",
    ("Privatforbrug", "Tobak & alkohol"): "Expenses:Food:Alcohol",
    ("Privatforbrug", "Tips & lotto"): "Expenses:Entertainment:Gambling",
    ("Privatforbrug", "Andet privatforbrug"): "Expenses:Shopping:Other",
    ("Privatforbrug", "Babyudstyr"): "Expenses:Kids:Baby",
    ("Privatforbrug", "Spil & legetøj"): "Expenses:Kids:Toys",
    ("Privatforbrug", "Hus & havehjælp"): "Expenses:House:Help",
    # Andre leveomkostninger
    ("Andre leveomkostninger", "Apotek & medicin"): "Expenses:Health:Pharmacy",
    ("Andre leveomkostninger", "Behandling & læger"): "Expenses:Health:Doctor",
    ("Andre leveomkostninger", "Briller & kontaktlinser"): "Expenses:Health:Vision",
    ("Andre leveomkostninger", "Fagforening & a-kasse"): "Expenses:Insurance:Union",
    ("Andre leveomkostninger", "Foreninger & kontingenter"): "Expenses:Subscriptions:Memberships",
    ("Andre leveomkostninger", "Institution"): "Expenses:Kids:Institution",
    ("Andre leveomkostninger", "Livs- & ulykkesforsikring"): "Expenses:Insurance:Life",
    ("Andre leveomkostninger", "Sundheds- & sygeforsikring"): "Expenses:Insurance:Health",
    ("Andre leveomkostninger", "TV & streaming"): "Expenses:Subscriptions:Streaming",
    ("Andre leveomkostninger", "Telefoni & internet"): "Expenses:Subscriptions:Telecom",
    # Ferie
    ("Ferie", "Ferieaktiviteter"): "Expenses:Travel:Activities",
    ("Ferie", "Fly & Hotel"): "Expenses:Travel:Transport",
    ("Ferie", "Billeje"): "Expenses:Travel:Car-Rental",
    ("Ferie", "Rejseforsikring"): "Expenses:Travel:Insurance",
    ("Ferie", "Sommerhus & camping"): "Expenses:Travel:Accommodation",
    # Diverse
    ("Diverse", "Bankgebyrer"): "Expenses:Bank:Fees",
    ("Diverse", "Bøder & afgifter"): "Expenses:Tax:Fines",
    ("Diverse", "Offentligt gebyr"): "Expenses:Tax:Fees",
    ("Diverse", "Restskat"): "Expenses:Tax:Back-Tax",
    ("Diverse", "Rykkergebyrer"): "Expenses:Bank:Late-Fees",
    ("Diverse", "Ukendt"): "Expenses:Other",
    # Lån & gæld
    ("Lån & gæld", "Forbrugslån"): "Expenses:Loans:Consumer",
    ("Lån & gæld", "Private lån (venner & familie)"): "Expenses:Loans:Private",
    ("Lån & gæld", "Studielån"): "Expenses:Loans:Student",
    ("Lån & gæld", "Udlånsrenter"): "Expenses:Loans:Interest",
    # Indkomst
    ("Indkomst", "Løn"): "Income:Salary",
    ("Indkomst", "Børnepenge"): "Income:ChildBenefit",
    ("Indkomst", "Feriepenge"): "Income:Holiday",
    ("Indkomst", "Dagpenge/overførselsindkomst"): "Income:Unemployment",
    ("Indkomst", "Overskydende skat"): "Income:Tax:Refund",
    ("Indkomst", "Renteindtægter"): "Income:Interest",
    ("Indkomst", "Anden indkomst"): "Income:Other",
    # Pension & Opsparing
    ("Pension & Opsparing", "Pensionsopsparing"): "Assets:Savings:Pension",
    ("Pension & Opsparing", "Værdipapirshandel"): "Assets:Savings:Investments",
    ("Pension & Opsparing", "Børneopsparing"): "Assets:Savings:Children",
    ("Pension & Opsparing", "Anden opsparing"): "Assets:Savings:Other",
    # Vis ikke (Exclude)
    ("Vis ikke", "Kontooverførsel"): "Assets:Transfer",
    ("Vis ikke", "Ignorer"): "Expenses:Uncategorized",
    # Empty categories
    ("", ""): "Expenses:Uncategorized",
}


def parse_date(s: str) -> date:
    """Parse DD-MM-YYYY to date."""
    return datetime.strptime(s, "%d-%m-%Y").date()


def parse_amount(s: str) -> str:
    """Parse Danish number format (comma decimal) to string with 2 decimal places."""
    s = s.strip()
    if not s:
        return "0.00"
    return f"{float(s.replace('.', '').replace(',', '.')):.2f}"


def sanitize_tag(tag: str) -> str:
    """Convert a tag string to a valid beancount tag (ASCII alphanumeric, hyphens, underscores)."""
    tag = tag.strip()
    # Transliterate common Danish characters
    for src, dst in [("æ", "ae"), ("ø", "oe"), ("å", "aa"), ("Æ", "Ae"), ("Ø", "Oe"), ("Å", "Aa")]:
        tag = tag.replace(src, dst)
    tag = re.sub(r"[^a-zA-Z0-9_-]", "-", tag)
    tag = re.sub(r"-+", "-", tag).strip("-")
    return tag if tag else None


def escape_str(s: str) -> str:
    """Escape a string for beancount (double quotes)."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def read_all_transactions():
    """Read all CSV files and return list of parsed transaction dicts."""
    transactions = []
    for csv_file in sorted(SPIIR_DIR.glob("*.csv")):
        with open(csv_file, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                # Use CustomDate if available, otherwise Date
                date_str = row.get("CustomDate", "").strip() or row["Date"]
                txn_date = parse_date(date_str)

                amount_str = row["Amount"]
                amount = parse_amount(amount_str)
                balance = parse_amount(row["Balance"])

                account_name = row["AccountName"]
                asset_account = ACCOUNT_MAP.get(account_name, f"Assets:Checking:{account_name}")

                main_cat = row["MainCategoryName"]
                cat_name = row["CategoryName"]
                cat_type = row["CategoryType"]
                category_account = CATEGORY_MAP.get(
                    (main_cat, cat_name), "Expenses:Uncategorized"
                )

                description = row["Description"].strip()
                spiir_id = row["Id"]

                # Parse tags
                tags = ["spiir"]
                raw_tags = row.get("Tags", "").strip()
                if raw_tags:
                    for t in raw_tags.split(","):
                        sanitized = sanitize_tag(t)
                        if sanitized:
                            tags.append(sanitized)

                transactions.append(
                    {
                        "date": txn_date,
                        "description": description,
                        "category_name": cat_name,
                        "asset_account": asset_account,
                        "category_account": category_account,
                        "amount": amount,
                        "balance": balance,
                        "spiir_id": spiir_id,
                        "tags": tags,
                        "account_name": account_name,
                        "raw_amount": amount_str,
                    }
                )
    return transactions


def compute_opening_balances(transactions):
    """Compute opening balance for each asset account from the first transaction."""
    # Group by asset account, find earliest transaction
    first_by_account = {}
    for txn in transactions:
        acct = txn["asset_account"]
        if acct not in first_by_account or txn["date"] < first_by_account[acct]["date"]:
            first_by_account[acct] = txn

    opening_balances = []
    for acct, txn in sorted(first_by_account.items()):
        # Balance before first transaction = balance_after - amount
        balance_after = float(txn["balance"])
        amount = float(txn["raw_amount"].replace(".", "").replace(",", "."))
        opening = balance_after - amount
        opening_balances.append(
            {
                "date": txn["date"],
                "account": acct,
                "amount": f"{opening:.2f}",
            }
        )
    return opening_balances


def format_transaction(txn):
    """Format a single transaction as beancount text."""
    tags_str = " ".join(f"#{t}" for t in txn["tags"])
    payee = escape_str(txn["description"])
    narration = escape_str(txn["category_name"])
    amount = txn["amount"]
    # Inverse amount for the category posting
    inv_amount = f"{-float(amount):.2f}"

    lines = [
        f'{txn["date"]} * "{payee}" "{narration}" {tags_str}',
        f'  spiir-id: "{txn["spiir_id"]}"',
        f"  {txn['asset_account']}  {amount} DKK",
        f"  {txn['category_account']}  {inv_amount} DKK",
    ]
    return "\n".join(lines)


def format_opening_balance(ob):
    """Format an opening balance transaction."""
    inv = f"{-float(ob['amount']):.2f}"
    lines = [
        f'{ob["date"]} * "Opening Balance" "" #spiir',
        f"  {ob['account']}  {ob['amount']} DKK",
        f"  Equity:Opening-Balances  {inv} DKK",
    ]
    return "\n".join(lines)


def write_year_files(transactions, opening_balances):
    """Write per-year .bean files."""
    # Group transactions by year
    by_year = {}
    for txn in transactions:
        year = txn["date"].year
        by_year.setdefault(year, []).append(txn)

    # Group opening balances by year
    ob_by_year = {}
    for ob in opening_balances:
        year = ob["date"].year
        ob_by_year.setdefault(year, []).append(ob)

    all_years = sorted(set(list(by_year.keys()) + list(ob_by_year.keys())))

    for year in all_years:
        path = BASE_DIR / f"{year}.bean"
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"; Spiir import for {year}\n")
            f.write(f"; Generated by import_spiir.py\n\n")

            # Opening balances first
            for ob in sorted(ob_by_year.get(year, []), key=lambda x: x["date"]):
                f.write(format_opening_balance(ob))
                f.write("\n\n")

            # Transactions sorted by date, then by spiir-id for stability
            year_txns = sorted(
                by_year.get(year, []), key=lambda x: (x["date"], x["spiir_id"])
            )
            for txn in year_txns:
                f.write(format_transaction(txn))
                f.write("\n\n")

        print(f"  Wrote {path.name}: {len(ob_by_year.get(year, []))} opening balances, {len(by_year.get(year, []))} transactions")

    return all_years


def collect_accounts(transactions, opening_balances):
    """Collect all accounts with their earliest date."""
    accounts = {}

    def track(account, d):
        if account not in accounts or d < accounts[account]:
            accounts[account] = d

    for txn in transactions:
        track(txn["asset_account"], txn["date"])
        track(txn["category_account"], txn["date"])

    for ob in opening_balances:
        track(ob["account"], ob["date"])
        track("Equity:Opening-Balances", ob["date"])

    return accounts


def update_main_bean(all_years, accounts):
    """Update main.bean with includes and open directives."""
    lines = []

    # Header
    lines.append('option "operating_currency" "DKK"')
    lines.append('option "booking_method" "FIFO"')
    lines.append("")

    # Include directives
    lines.append("; --- Spiir imports ---")
    for year in sorted(all_years):
        lines.append(f'include "{year}.bean"')
    lines.append("")

    # Open directives for all accounts
    lines.append("; --- Spiir accounts ---")
    for account, earliest_date in sorted(accounts.items()):
        lines.append(f"{earliest_date} open {account} DKK")
    lines.append("")

    MAIN_BEAN.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Updated {MAIN_BEAN.name}")


def main():
    print("Reading Spiir CSVs...")
    transactions = read_all_transactions()
    print(f"  Found {len(transactions)} transactions")

    print("Computing opening balances...")
    opening_balances = compute_opening_balances(transactions)
    for ob in opening_balances:
        print(f"  {ob['account']}: {ob['amount']} DKK on {ob['date']}")

    print("Writing year files...")
    all_years = write_year_files(transactions, opening_balances)

    print("Collecting accounts...")
    accounts = collect_accounts(transactions, opening_balances)
    print(f"  Found {len(accounts)} unique accounts")

    print("Updating main.bean...")
    update_main_bean(all_years, accounts)

    print("Done!")


if __name__ == "__main__":
    main()
