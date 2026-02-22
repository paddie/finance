import decimal
from . import constants
from typing import Optional, Callable


CATEGORY_MAP = {
    # Husholdning
    "dagligvarer": "Expenses:Food:Groceries",
    "kantine- & frokostordning": "Expenses:Food:Canteen",
    "kiosk, bager & specialbutikker": "Expenses:Food:Restaurant",
    # transport
    "bilforsikring & autohjælp": "Expenses:Car:Insurance",
    "brændstof": "Expenses:Car:Gas",
    "parkering": "Expenses:Car:Parking",
    "bus, tog, færge o.l.": "Expenses:Transport:Public",
    "taxi": "Expenses:Travel:Taxi",
    "ejerafgift/grøn afgift": "Expenses:Car:Tax",
    "værksted & reservedele": "Expenses:Car:Service",
    "anden transport": "Expenses:Transport:Other",
    # bolig
    "boliglån/husleje": "Expenses:House:Mortgage",
    "el, vand, varme & renovation": "Expenses:House",
    "ombygning & vedligehold": "Expenses:House:Renovation",
    "husforsikring": "Expenses:House:Insurance",
    "ejendomsskat": "Expenses:House:Tax",
    "ejerforening": "Expenses:House:Association",
    "have & planter": "Expenses:House:Garden",
    "alarmsystem": "Expenses:House:Alarm",
    "andre boligudgifter": "Expenses:House:Other",
    "indbo- & familieforsikring": "Expenses:House:Contents-Insurance",
    # privatforbrug
    "tøj, sko & accessories": "Expenses:Shopping:Clothing",
    "elektronik & computerudstyr": "Expenses:Shopping:Electronics",
    "møbler & boligudstyr": "Expenses:Shopping:Furniture",
    "bar, cafe & restaurant": "Expenses:Food:Restaurant",
    "fastfood & takeaway": "Expenses:Food:Takeaway",
    "biograf, koncerter & forlystelser": "Expenses:Entertainment:Events",
    "film, musik & læsestof": "Expenses:Entertainment:Media",
    "sport & fritid": "Expenses:Entertainment:Sports",
    "hobby & sportsudstyr": "Expenses:Shopping:Sports",
    "frisør & personlig pleje": "Expenses:Shopping:Personal-Care",
    "gaver & velgørenhed": "Expenses:Gifts",
    "kontanthævning & check": "Expenses:Cash",
    "online services & software": "Expenses:Subscriptions:Software",
    "serviceydelser & rådgivning": "Expenses:Services",
    "tobak & alkohol": "Expenses:Food:Alcohol",
    "tips & lotto": "Expenses:Entertainment:Gambling",
    "andet privatforbrug": "Expenses:Shopping:Other",
    "babyudstyr": "Expenses:Kids:Baby",
    "spil & legetøj": "Expenses:Kids:Toys",
    "hus & havehjælp": "Expenses:House:Help",
    # andre leveomkostninger
    "apotek & medicin": "Expenses:Health:Medicin",
    "behandling & læger": "Expenses:Health:Doctor",
    "briller & kontaktlinser": "Expenses:Health:Vision",
    "fagforening & a-kasse": "Expenses:Insurance:Union",
    "foreninger & kontingenter": "Expenses:Subscriptions:Memberships",
    "institution": "Expenses:Kids:Institution",
    "livs- & ulykkesforsikring": "Expenses:Insurance:Life",
    "sundheds- & sygeforsikring": "Expenses:Insurance:Health",
    "tv & streaming": "Expenses:Subscriptions:Streaming",
    "telefoni & internet": "Expenses:Subscriptions:Telecom",
    # ferie
    "ferieaktiviteter": "Expenses:Travel",
    "fly & hotel": "Expenses:Travel",
    "billeje": "Expenses:Travel:Carrental",
    "rejseforsikring": "Expenses:Travel:Insurance",
    "sommerhus & camping": "Expenses:Travel:Accommodation",
    # diverse
    "bankgebyrer": "Expenses:Bank:Fees",
    "bøder & afgifter": "Expenses:Tax:Fines",
    "offentligt gebyr": "Expenses:Tax:Fees",
    "restskat": "Expenses:Tax:Back-Tax",
    "rykkergebyrer": "Expenses:Bank:Late-Fees",
    # lån & gæld
    "forbrugslån": "Expenses:Loans:Consumer",
    "private lån (venner & familie)": "Expenses:Loans:Private",
    "studielån": "Expenses:Loans:Student",
    "udlånsrenter": "Expenses:Loans:Interest",
    # indkomst
    "løn": "Income:Salary",
    "børnepenge": "Income:Childbenefit",
    "feriepenge": "Income:Holiday",
    "dagpenge/overførselsindkomst": "Income:Unemployment",
    "overskydende skat": "Income:Tax:Refund",
    "renteindtægter": "Income:Interest",
    "anden indkomst": "Income:Other",
    # pension & opsparing
    "pensionsopsparing": "Assets:Savings:Pension",
    "værdipapirshandel": "Assets:Savings:Investments",
    "børneopsparing": "Assets:Savings:Children",
    "anden opsparing": "Assets:Savings:Other",
    # vis ikke (exclude)
    "kontooverførsel": "Assets:Transfer",
    "ignorer": "Expenses:Other",
    # empty categories
    "ukendt": "Expenses:Other",
}


def kids_rules(
    asset_account: str, r : constants.SpiirRow
) -> Optional[str]:
    if any(keyword in r.description for keyword in {
        "boerneloppen",
    }):
        return "Expenses:Kids:Clothing"

    if "experimentarium" in r.description:
        return "Expenses:Kids:Activities"

    if "mobilepay ella hollesen schefer" in r.description:
        return "Expenses:Kids:Babysitter"

    if "hvidovre kommune" in r.description or "institution" in r.category_name:
        return "Expenses:Kids:Daycare"

    return None

def food_rules(
    asset_account: str, r : constants.SpiirRow
) -> Optional[str]:
    if any(keyword in r.description for keyword in {
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
    }):
        return "Expenses:Food:Groceries"

    return None


def car_rules(
    asset_account: str, r : constants.SpiirRow
) -> Optional[str]:
    # PARKING
    if any(keyword in r.description for keyword in {
        "parkering",
        "parking",
        "apcoa",
        "parkman",
        "easypark",
        "easy park",
        "q-park",
    }):
        return "Expenses:Car:Parking"

    # SERVICE
    if any(keyword in r.description for keyword in {
        "værksted",
        "service",
        "autotal",
        "bilpleje",
        "autoservice",
        "quickpoint",
    }):
        return "Expenses:Car:Service"

    # GAS
    if any(keyword in r.description for keyword in {
        "uno-x",
        "q8 service",
        "shell",
        "oil! tank go",
        "ingo",
        "circlek",
        "circle k",
    }):
        return "Expenses:Car:Gas"
    return None


def house_rules(
    asset_account: str, r : constants.SpiirRow
) -> Optional[str]:
    RENOVATION_KEYWORDS = {
        "bauhaus",
        "jem & fix",
        "silvan",
        "bilka",
        "stark",
    }
    if any(keyword in r.description for keyword in RENOVATION_KEYWORDS):
        return "Expenses:House:Renovation"

    UTILITY_KEYWORDS = {
        "fd hvodovre",
        "hofor",
        "evida service nord",
        "nettopower",
        "zacho-lind",
    }
    if any(keyword in r.description for keyword in UTILITY_KEYWORDS):
        return "Expenses:House:Utilities"

    if "ikea" in r.description:
        return "Expenses:House:Furniture"

    if "spidskloak" in r.description:
        return "Expenses:House:Plumbing"

    if "nedbetaling huslån - prm" in r.description:
        return "Liabilities:House:Mortgage"

    if "realkredit danmark" in r.description:
        return "Liabilities:House:Mortgage"


def investment_rules(
    asset_account: str, r : constants.SpiirRow
) -> Optional[str]:
    if "saxo" in r.description and "ask" in r.description:
        return "Assets:Investments:ASK"
    
    if "saxo" in r.description and "skat" in r.description:
        return "Assets:Investments:Skat"
    
    if "nordnet" in r.description and "skat" in r.description:
        return "Assets:Investments:Skat"

    if "aldersopsparing" in r.description:
        return "Assets:Pension:Aldersopsparing"

    if "ratepension" in r.description:
        return "Assets:Pension:Ratepension"

    if "livrente" in r.description:
        return "Assets:Pension:Livrente"

    if "nordnet aktiedepot" in r.description:
        return "Assets:Investments:Nordnet:Aktiedepot"



def shopping_rules(
    asset_account: str, r : constants.SpiirRow
) -> Optional[str]:
    SHOES_CLOTHING_KEYWORDS = {
        "friluftsland",
        "salomon",
        "spejder sport",
        "fjeld & fritid",
        "fjællræven",
    }
    if any(keyword in r.description for keyword in SHOES_CLOTHING_KEYWORDS):
        return "Expenses:Shopping:Gear"

    if "xeroshoes" in r.description:
        return "Expenses:Shopping:Gear:Shoes"

    if "amazon" in r.description:
        return "Expenses:Shopping"

    GAMING_KEYWORDS = {
        "playstation",
        "xbox",
        "nintendo",
        "steam",
    }

    if any(keyword in r.description for keyword in GAMING_KEYWORDS):
        return "Expenses:Entertainment:Gaming"

    return None

def transfers_rules(
    asset_account: str, r : constants.SpiirRow
) -> Optional[str]:
    # PRM
    if r.description.endswith(" - prm"):
        return "Expenses:Transfers"

    if r.description.endswith(" - lah") or r.description.endswith("lah"):
        return "Equity:LAH"
    
    if "til dagligvarer" in r.description and r.account_name == "primary":
        return "Expenses:Transfers"
    
    if "til dagligvarer" in r.description and r.account_name == "kærestekonto" and r.counter_entry_id:
        return "Expenses:Food:Groceries"
    
    # overførsel til dagligvarer fra primary
    if "til dagligvarer" in r.description and r.account_name == "kærestekonto" and not r.counter_entry_id:
        return "Expenses:Food:Groceries"

    # vil kun ske på kærestekontoen
    if "fra lee ann hollesen" in r.description and r.account_name == "primary":
        return "Equity:LAH"
    
    # overførsler til dagligvarer til kærestekonto fra LA
    # udover den normale overførsel
    if "til dagligvarer" in r.description and r.account_type == "kærestekonto" and not r.counter_entry_id == "":
        return "Equity:LAH"

    return None


def _classify_rules(
    asset_account: str,
    r : constants.SpiirRow,
    *rules: Callable[[str, SpiirRow], Optional[str]],
) -> str:
    for rule in rules:
        result = rule(asset_account, r)
        if result is not None:
            return result

    fallback = CATEGORY_MAP.get(r.category_name, "Expenses:Other")
    if fallback != "Expenses:Other":
        return fallback
    
    if r.description.startswith("mobilepay"):
        return "Expenses:Other:Mobilepay"

    if asset_account == constants.DAGLIGVARER_ACCOUNT:
        return "Expenses:Other:Dagligvarer"
    if asset_account == constants.PRIMARY_ACCOUNT:
        return "Expenses:Other:Primary"
    if asset_account == constants.FIXED_ACCOUNT:
        return "Expenses:Other:Fixed"
    
    return "Expenses:Other"


def classify_account(asset_account: str, r : constants.SpiirRow) -> str:
    # if any of the grocery keywords are in the description, classify as groceries
    return _classify_rules(
        asset_account,
        r,
        food_rules,
        car_rules,
        kids_rules,
        house_rules,
        investment_rules,
        shopping_rules,
        transfers_rules,
    )
