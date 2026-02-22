import constants
from typing import Optional, Callable


CATEGORY_MAP = {
    # Husholdning
    "Dagligvarer": "Expenses:Food:Groceries",
    "Kantine- & frokostordning": "Expenses:Food:Canteen",
    "Kiosk, bager & specialbutikker": "Expenses:Food:Restaurant",
    # Transport
    "Bilforsikring & autohjælp": "Expenses:Car:Insurance",
    "Brændstof": "Expenses:Car:Gas",
    "Parkering": "Expenses:Car:Parking",
    "Bus, tog, færge o.l.": "Expenses:Transport:Public",
    "Taxi": "Expenses:Travel:Taxi",
    "Ejerafgift/grøn afgift": "Expenses:Car:Tax",
    "Værksted & reservedele": "Expenses:Car:Service",
    "Anden transport": "Expenses:Transport:Other",
    # Bolig
    "Boliglån/husleje": "Expenses:House:Mortgage",
    "El, vand, varme & renovation": "Expenses:House",
    "Ombygning & vedligehold": "Expenses:House:Renovation",
    "Husforsikring": "Expenses:House:Insurance",
    "Ejendomsskat": "Expenses:House:Tax",
    "Ejerforening": "Expenses:House:Association",
    "Have & planter": "Expenses:House:Garden",
    "Alarmsystem": "Expenses:House:Alarm",
    "Andre boligudgifter": "Expenses:House:Other",
    "Indbo- & familieforsikring": "Expenses:House:Contents-Insurance",
    # Privatforbrug
    "Tøj, sko & accessories": "Expenses:Shopping:Clothing",
    "Elektronik & computerudstyr": "Expenses:Shopping:Electronics",
    "Møbler & boligudstyr": "Expenses:Shopping:Furniture",
    "Bar, cafe & restaurant": "Expenses:Food:Restaurant",
    "Fastfood & takeaway": "Expenses:Food:Takeaway",
    "Biograf, koncerter & forlystelser": "Expenses:Entertainment:Events",
    "Film, musik & læsestof": "Expenses:Entertainment:Media",
    "Sport & fritid": "Expenses:Entertainment:Sports",
    "Hobby & sportsudstyr": "Expenses:Shopping:Sports",
    "Frisør & personlig pleje": "Expenses:Shopping:Personal-Care",
    "Gaver & velgørenhed": "Expenses:Gifts",
    "Kontanthævning & check": "Expenses:Cash",
    "Online services & software": "Expenses:Subscriptions:Software",
    "Serviceydelser & rådgivning": "Expenses:Services",
    "Tobak & alkohol": "Expenses:Food:Alcohol",
    "Tips & lotto": "Expenses:Entertainment:Gambling",
    "Andet privatforbrug": "Expenses:Shopping:Other",
    "Babyudstyr": "Expenses:Kids:Baby",
    "Spil & legetøj": "Expenses:Kids:Toys",
    "Hus & havehjælp": "Expenses:House:Help",
    # Andre leveomkostninger
    "Apotek & medicin": "Expenses:Health:Pharmacy",
    "Behandling & læger": "Expenses:Health:Doctor",
    "Briller & kontaktlinser": "Expenses:Health:Vision",
    "Fagforening & a-kasse": "Expenses:Insurance:Union",
    "Foreninger & kontingenter": "Expenses:Subscriptions:Memberships",
    "Institution": "Expenses:Kids:Institution",
    "Livs- & ulykkesforsikring": "Expenses:Insurance:Life",
    "Sundheds- & sygeforsikring": "Expenses:Insurance:Health",
    "TV & streaming": "Expenses:Subscriptions:Streaming",
    "Telefoni & internet": "Expenses:Subscriptions:Telecom",
    # Ferie
    "Ferieaktiviteter": "Expenses:Travel",
    "Fly & Hotel": "Expenses:Travel",
    "Billeje": "Expenses:Travel:CarRental",
    "Rejseforsikring": "Expenses:Travel:Insurance",
    "Sommerhus & camping": "Expenses:Travel:Accommodation",
    # Diverse
    "Bankgebyrer": "Expenses:Bank:Fees",
    "Bøder & afgifter": "Expenses:Tax:Fines",
    "Offentligt gebyr": "Expenses:Tax:Fees",
    "Restskat": "Expenses:Tax:Back-Tax",
    "Rykkergebyrer": "Expenses:Bank:Late-Fees",
    "Ukendt": "Expenses:Other",
    # Lån & gæld
    "Forbrugslån": "Expenses:Loans:Consumer",
    "Private lån (venner & familie)": "Expenses:Loans:Private",
    "Studielån": "Expenses:Loans:Student",
    "Udlånsrenter": "Expenses:Loans:Interest",
    # Indkomst
    "Løn": "Income:Salary",
    "Børnepenge": "Income:ChildBenefit",
    "Feriepenge": "Income:Holiday",
    "Dagpenge/overførselsindkomst": "Income:Unemployment",
    "Overskydende skat": "Income:Tax:Refund",
    "Renteindtægter": "Income:Interest",
    "Anden indkomst": "Income:Other",
    # Pension & Opsparing
    "Pensionsopsparing": "Assets:Savings:Pension",
    "Værdipapirshandel": "Assets:Savings:Investments",
    "Børneopsparing": "Assets:Savings:Children",
    "Anden opsparing": "Assets:Savings:Other",
    # Vis ikke (Exclude)
    "Kontooverførsel": "Assets:Transfer",
    "Ignorer": "Expenses:Other",
    # Empty categories
    "": "Expenses:Other",
}


def kids_rules(
    asset_account: str, description: str, category_name: str
) -> Optional[str]:
    CLOTHING_KEYWORDS = {
        "boerneloppen",
    }
    if any(keyword in description for keyword in CLOTHING_KEYWORDS):
        return "Expenses:Kids:Clothing"

    if "EXPERIMENTARIUM" in description:
        return "Expenses:Kids:Activities"

    if "MobilePay Ella Hollesen Schefer" in description:
        return "Expenses:Kids:Babysitter"

    if "hvidovre kommune" in description or "institution" in category_name:
        return "Expenses:Kids:Daycare"

    return None


def food_rules(
    asset_account: str, description: str, category_name: str
) -> Optional[str]:
    GROCERY_KEYWORDS = {
        "lidl",
        "kvickly",
        "netto",
        "coop365",
        "365discount",
        "superb",
        "rema 1000",
        "dagli brugsen",
        "7-eleven",
        "meny",
        "supermercados",
        "ume asian",
        "market",
        "den kinesiske køb",
        "denkinesiskekoebmand",
        "kft koebenhavn",
        "kft jylland-kbh",
        "supermarked",
    }
    if any(keyword in description for keyword in GROCERY_KEYWORDS):
        return "Expenses:Food:Groceries"

    if "til dagligvarer" in description:
        return "Expenses:Transfers:PRM"

    return None


def car_rules(
    asset_account: str, description: str, category_name: str
) -> Optional[str]:
    # apcoa|EasyPark|parkman|EASY PARK|Parkering|Q-Park
    PARKING = {
        "parkering",
        "parking",
        "apcoa",
        "parkman",
        "easypark",
        "easy park",
        "q-park",
    }
    if any(keyword in description for keyword in PARKING):
        return "Expenses:Car:Parking"

    SERVICE = {
        "værksted",
        "service",
        "autotal",
        "bilpleje",
        "autoservice",
        "quickpoint",
    }
    if any(keyword in description for keyword in SERVICE):
        return "Expenses:Car:Service"

    GAS = {
        "uno-x",
        "q8 service",
        "shell",
        "oil! tank go",
        "ingo",
        "circlek",
        "circle k",
    }
    if any(keyword in description for keyword in GAS):
        return "Expenses:Car:Gas"
    return None


def house_rules(
    asset_account: str, description: str, category_name: str
) -> Optional[str]:
    RENOVATION_KEYWORDS = {
        "bauhaus",
        "jem & fix",
        "silvan",
        "bilka",
        "stark",
    }
    if any(keyword in description for keyword in RENOVATION_KEYWORDS):
        return "Expenses:House:Renovation"

    UTILITY_KEYWORDS = {
        "fd hvodovre",
        "hofor",
        "evida service nord",
        "nettopower",
        "zacho-lind",
    }
    if any(keyword in description for keyword in UTILITY_KEYWORDS):
        return "Expenses:House:Utilities"

    if "ikea" in description:
        return "Expenses:House:Furniture"

    if "spidskloak" in description:
        return "Expenses:House:Plumbing"

    if "nedbetaling huslån - prm" in description:
        return "Liabilities:House:Mortgage"

    if "realkredit danmark" in description:
        return "Liabilities:House:Mortgage"

    if description.endswith(" - prm"):
        return "Expenses:Transfers:PRM"

    if description.endswith(" - lah") or description.endswith("lah"):
        return "Assets:LAH"


def investment_rules(
    asset_account: str, description: str, category_name: str
) -> Optional[str]:
    if "saxo" in description and "ask" in description:
        return "Assets:Investments:Saxo:ASK"

    if "aldersopsparing" in description:
        return "Assets:Pension:Aldersopsparing"

    if "ratepension" in description:
        return "Assets:Pension:Ratepension"

    if "livrente" in description:
        return "Assets:Pension:Livrente"

    if "nordnet aktiedepot" in description:
        return "Assets:Investments:Nordnet:Aktiedepot"


def leeann_rules(
    asset_account: str, description: str, category_name: str
) -> Optional[str]:
    if "fra lee ann hollesen" in description:
        return "Expenses:LeeAnn"
    return None


def shopping_rules(
    asset_account: str, description: str, category_name: str
) -> Optional[str]:
    SHOES_CLOTHING_KEYWORDS = {
        "friluftsland",
        "salomon",
        "spejder sport",
        "fjeld & fritid",
        "fjællræven",
    }
    if any(keyword in description for keyword in SHOES_CLOTHING_KEYWORDS):
        return "Expenses:Shopping:Gear"

    if "xeroshoes" in description:
        return "Expenses:Shopping:Gear:Shoes"

    if "amazon" in description:
        return "Expenses:Shopping"

    GAMING_KEYWORDS = {
        "playstation",
        "xbox",
        "nintendo",
        "steam",
    }

    if any(keyword in description for keyword in GAMING_KEYWORDS):
        return "Expenses:Entertainment:Gaming"

    return None


def _classify_rules(
    asset_account: str,
    description: str,
    category_name: str,
    *rules: Callable[[str, str, str], Optional[str]],
) -> str:
    for rule in rules:
        result = rule(asset_account, description, category_name)
        if result is not None:
            return result

    fallback = CATEGORY_MAP.get(category_name, "Expenses:Other")

    if fallback == "Expenses:Other":
        if asset_account == constants.DAGLIGVARER_ACCOUNT:
            return "Expenses:Other:Dagligvarer"
        if asset_account == constants.PRIMARY_ACCOUNT:
            return "Expenses:Other:Primary"
        if asset_account == constants.FIXED_ACCOUNT:
            return "Expenses:Other:Fixed"

    return fallback


def classify_account(asset_account: str, description: str, category_name: str) -> str:
    # if any of the grocery keywords are in the description, classify as groceries
    return _classify_rules(
        asset_account,
        description,
        category_name,
        food_rules,
        car_rules,
        kids_rules,
        house_rules,
        leeann_rules,
        investment_rules,
        shopping_rules,
    )
