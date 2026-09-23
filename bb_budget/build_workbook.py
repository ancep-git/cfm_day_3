"""Build BB_Budget.xlsx for the "Ball Bearing Contract Auction" case.

Every calculated cell is a live Excel formula that points at an input cell, so
the workbook stays usable in Excel without re-running this script.

Usage:  python build_workbook.py [output_path]
"""

import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.workbook.properties import CalcProperties
from openpyxl.worksheet.datavalidation import DataValidation

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("BB_Budget.xlsx")

# ----------------------------------------------------------------------------
# Case data (typed into input cells only)
# ----------------------------------------------------------------------------
Y1_CONTRACTS = [
    # id, spec, accepted qty, price per BB
    ("C05", "Silver", 15, 18000),
    ("C08", "Silver", 40, 11000),
    ("C09", "Copper", 40, 6500),
]
SPECS = ["Blue", "Silver", "Copper"]
TIERS = [  # lower bound, Blue, Silver, Copper
    (1, 7000, 6500, 5500),
    (11, 6500, 6000, 5000),
    (21, 5500, 5500, 4000),
    (31, 5000, 4500, 3000),
    (41, 4000, 3500, 2000),
]
FIXED = [
    ("Factory rent", 50000),
    ("Management & administration", 40000),
    ("Machine maintenance", 35000),
    ("Utilities & insurance", 20000),
    ("Office & marketing", 15000),
    ("Depreciation", 40000),
]
N_ROWS = 30          # contract rows per year sheet (3 used in Y1 + 27 spare)
FIRST = 5            # first contract row on the Contracts sheets
LAST = FIRST + N_ROWS - 1
TOTAL_ROW = LAST + 2

# ----------------------------------------------------------------------------
# Styles
# ----------------------------------------------------------------------------
FONT = "Arial"
F_BASE = Font(name=FONT, size=10)
F_BOLD = Font(name=FONT, size=10, bold=True)
F_TITLE = Font(name=FONT, size=14, bold=True)
F_NOTE = Font(name=FONT, size=9, italic=True, color="595959")
F_INPUT = Font(name=FONT, size=10, color="0000FF")
F_LINK = Font(name=FONT, size=10, color="008000")
F_LINK_BOLD = Font(name=FONT, size=10, color="008000", bold=True)
F_HEAD = Font(name=FONT, size=10, bold=True, color="FFFFFF")

FILL_INPUT = PatternFill("solid", fgColor="DDEBF7")
FILL_CONFIRM = PatternFill("solid", fgColor="FFFF00")
FILL_HEAD = PatternFill("solid", fgColor="1F3864")
FILL_TOTAL = PatternFill("solid", fgColor="F2F2F2")
FILL_ORANGE = PatternFill("solid", fgColor="FFC000")

THIN = Side(style="thin", color="BFBFBF")
TOP_LINE = Border(top=Side(style="thin", color="000000"))

USD = '$#,##0;[Red]($#,##0);"-"'
QTY = '#,##0;[Red](#,##0);"-"'
PCT = '0.0%;[Red]-0.0%;"-"'
RATE = "0.0%"
COEF = "0.00"

WRAP_CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)


def style(cell, font=F_BASE, fmt=None, fill=None, align=None, border=None):
    cell.font = font
    if fmt:
        cell.number_format = fmt
    if fill:
        cell.fill = fill
    if align:
        cell.alignment = align
    if border:
        cell.border = border
    return cell


def put(ws, ref, value, **kw):
    ws[ref] = value
    return style(ws[ref], **kw)


def inp(ws, ref, value, fmt=None):
    return put(ws, ref, value, font=F_INPUT, fmt=fmt, fill=FILL_INPUT)


def header_row(ws, row, labels, start_col=1):
    for i, text in enumerate(labels):
        put(ws, f"{get_column_letter(start_col + i)}{row}", text,
            font=F_HEAD, fill=FILL_HEAD, align=WRAP_CENTER)
    ws.row_dimensions[row].height = 42


def add_name(wb, name, ref):
    wb.defined_names[name] = DefinedName(name, attr_text=ref)


wb = Workbook()

# ----------------------------------------------------------------------------
# Inputs
# ----------------------------------------------------------------------------
ws = wb.active
ws.title = "Inputs"
ws.sheet_properties.tabColor = "4472C4"
put(ws, "A1", "Ball Bearing Contract Auction: inputs", font=F_TITLE)
put(ws, "A2", "Blue text on a light-blue fill = input you can change. "
              "Yellow fill = value to confirm. Black = formula. "
              "All values from the case brief.", font=F_NOTE)

put(ws, "A4", "Production rules", font=F_BOLD)
put(ws, "A5", "Rejection rate (share of BBs produced that fail inspection)")
inp(ws, "B5", 0.15, RATE)
put(ws, "C5", "Production = ROUNDUP(accepted / (1 - rate), 0). Customer pays for accepted BBs only.",
    font=F_NOTE)
put(ws, "A6", "Wage coefficient (wages = raw materials used x coefficient)")
inp(ws, "B6", 1.8, COEF)
put(ws, "A7", "Gold price per BB (flat, announced after the auction)")
inp(ws, "B7", 5500, USD)
put(ws, "C7", "Pick 4,500 / 5,000 / 5,500 from the dropdown. Default 5,500 until announced.",
    font=F_NOTE)
dv_gold = DataValidation(type="list", formula1='"4500,5000,5500"', allow_blank=False,
                         showErrorMessage=True, errorTitle="Gold price",
                         error="Choose 4,500, 5,000 or 5,500.")
ws.add_data_validation(dv_gold)
dv_gold.add("B7")
put(ws, "A8", "Contract price range: minimum per BB")
inp(ws, "B8", 16000, USD)
put(ws, "A9", "Contract price range: maximum per BB")
inp(ws, "B9", 26000, USD)
put(ws, "C8", "Prices outside this range are flagged orange on the Contracts sheets.", font=F_NOTE)

put(ws, "A11", "Raw-material price per BB (all-units tiers)", font=F_BOLD)
put(ws, "A12", "The tier reached by one contract's purchase-order quantity "
               "(= its production quantity) sets the price for every BB in that order.",
    font=F_NOTE)
header_row(ws, 13, ["Qty ordered (lower bound)"] + SPECS)
for r, tier in enumerate(TIERS, start=14):
    for c, v in enumerate(tier, start=1):
        inp(ws, f"{get_column_letter(c)}{r}", v, QTY if c == 1 else USD)
TIER_END = 13 + len(TIERS)
put(ws, f"A{TIER_END + 1}", "Gold does not use this table; it uses the Gold price in B7.",
    font=F_NOTE)

FX_START = TIER_END + 3
put(ws, f"A{FX_START}", "Fixed operating expenses per year", font=F_BOLD)
for i, (label, amount) in enumerate(FIXED, start=FX_START + 1):
    put(ws, f"A{i}", label)
    inp(ws, f"B{i}", amount, USD)
FX_TOTAL = FX_START + len(FIXED) + 1
put(ws, f"A{FX_TOTAL}", "Total fixed operating expenses", font=F_BOLD)
put(ws, f"B{FX_TOTAL}", f"=SUM(B{FX_START + 1}:B{FX_TOTAL - 1})", font=F_BOLD, fmt=USD,
    border=TOP_LINE)

MK = FX_TOTAL + 2
put(ws, f"A{MK}", "Market size", font=F_BOLD)
put(ws, f"A{MK + 1}", "Year 1 market size")
inp(ws, f"B{MK + 1}", 5300000, USD)
put(ws, f"A{MK + 2}", "Year 2 growth over Year 1")
inp(ws, f"B{MK + 2}", 0.20, RATE)
put(ws, f"A{MK + 3}", "Year 3 growth over Year 2")
inp(ws, f"B{MK + 3}", 0.10, RATE)
put(ws, f"A{MK + 4}", "Year 2 market size")
put(ws, f"B{MK + 4}", f"=B{MK + 1}*(1+B{MK + 2})", fmt=USD)
put(ws, f"A{MK + 5}", "Year 3 market size")
put(ws, f"B{MK + 5}", f"=B{MK + 4}*(1+B{MK + 3})", fmt=USD)
MARKET = {1: f"Inputs!$B${MK + 1}", 2: f"Inputs!$B${MK + 4}", 3: f"Inputs!$B${MK + 5}"}

ws.column_dimensions["A"].width = 58
for col in "BCD":
    ws.column_dimensions[col].width = 14
ws.column_dimensions["E"].width = 14
ws.freeze_panes = "A4"

add_name(wb, "RejRate", "Inputs!$B$5")
add_name(wb, "WageCoef", "Inputs!$B$6")
add_name(wb, "GoldPrice", "Inputs!$B$7")
add_name(wb, "PriceMin", "Inputs!$B$8")
add_name(wb, "PriceMax", "Inputs!$B$9")
add_name(wb, "TierQty", f"Inputs!$A$14:$A${TIER_END}")
add_name(wb, "TierSpecs", "Inputs!$B$13:$D$13")
add_name(wb, "TierPrices", f"Inputs!$B$14:$D${TIER_END}")
add_name(wb, "FixedTotal", f"Inputs!$B${FX_TOTAL}")

# ----------------------------------------------------------------------------
# Contracts Yn
# ----------------------------------------------------------------------------
C_HEAD = ["Contract ID", "Spec", "Accepted qty (BB)", "Price per BB ($)",
          "Production qty (BB)", "Rejected qty (BB)", "RM price per BB ($)",
          "Revenue ($)", "Raw materials ($)", "Wages ($)", "Other direct ($)",
          "Contribution margin ($)", "CM %", "Break-even price per accepted BB ($)",
          "Price vs break-even ($)"]
C_WIDTH = [12, 10, 11, 12, 12, 11, 12, 13, 13, 13, 12, 14, 9, 15, 13]
INPUT_COLS = {"A", "B", "C", "D", "K"}


def contract_formulas(r):
    blank = f'IF($A{r}="",""'
    return {
        "E": f"={blank},ROUNDUP(C{r}/(1-RejRate),0))",
        "F": f"={blank},E{r}-C{r})",
        # All-units tier from this contract's own order qty; Gold is a flat price.
        "G": f'={blank},IF(B{r}="Gold",GoldPrice,'
             f"INDEX(TierPrices,MATCH(E{r},TierQty,1),MATCH(B{r},TierSpecs,0))))",
        "H": f"={blank},C{r}*D{r})",
        "I": f"={blank},E{r}*G{r})",
        "J": f"={blank},I{r}*WageCoef)",
        "L": f"={blank},H{r}-I{r}-J{r}-N(K{r}))",
        "M": f'=IF(OR($A{r}="",N(H{r})=0),"",L{r}/H{r})',
        "N": f'=IF(OR($A{r}="",N(C{r})=0),"",(E{r}*G{r}*(1+WageCoef)+N(K{r}))/C{r})',
        "O": f'=IF(OR($A{r}="",N{r}=""),"",D{r}-N{r})',
    }


def col_fmt(col):
    if col in "CEF":
        return QTY
    if col == "M":
        return PCT
    if col in "AB":
        return None
    return USD


def build_contracts(year, contracts):
    ws = wb.create_sheet(f"Contracts Y{year}")
    ws.sheet_properties.tabColor = "70AD47"
    put(ws, "A1", f"Year {year} contracts won", font=F_TITLE)
    put(ws, "A2", "Type Contract ID, Spec, Accepted qty and Price (blue cells) in any empty row; "
                  "every other column calculates. Each contract is its own purchase order.",
        font=F_NOTE)
    put(ws, "A3", "Orange price = outside the case price range (Inputs B8:B9). "
                  "Other direct defaults to 0.", font=F_NOTE)
    header_row(ws, 4, C_HEAD)

    dv_spec = DataValidation(type="list", formula1='"Blue,Silver,Copper,Gold"', allow_blank=True,
                             showErrorMessage=True, errorTitle="Spec",
                             error="Choose Blue, Silver, Copper or Gold.")
    ws.add_data_validation(dv_spec)
    dv_spec.add(f"B{FIRST}:B{LAST}")

    for i, r in enumerate(range(FIRST, LAST + 1)):
        data = contracts[i] if i < len(contracts) else None
        for col in "ABCDK":
            cell = ws[f"{col}{r}"]
            style(cell, font=F_INPUT, fmt=col_fmt(col), fill=FILL_INPUT)
            cell.border = Border(bottom=THIN)
        if data:
            for col, v in zip("ABCD", data):
                ws[f"{col}{r}"] = v
            ws[f"K{r}"] = 0
        for col, f in contract_formulas(r).items():
            put(ws, f"{col}{r}", f, fmt=col_fmt(col), border=Border(bottom=THIN))

    t = TOTAL_ROW
    put(ws, f"A{t}", "Total", font=F_BOLD, fill=FILL_TOTAL)
    for col in "BCDEFGHIJKLMNO":
        style(ws[f"{col}{t}"], font=F_BOLD, fill=FILL_TOTAL, border=TOP_LINE, fmt=col_fmt(col))
    for col in "CEFHIJKL":
        ws[f"{col}{t}"] = f"=SUM({col}{FIRST}:{col}{LAST})"
    ws[f"M{t}"] = f'=IF(N(H{t})=0,"",L{t}/H{t})'

    ws.conditional_formatting.add(
        f"D{FIRST}:D{LAST}",
        FormulaRule(formula=[f'AND(ISNUMBER(D{FIRST}),OR(D{FIRST}<PriceMin,D{FIRST}>PriceMax))'],
                    fill=FILL_ORANGE, stopIfTrue=False))

    for i, w in enumerate(C_WIDTH, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = f"B{FIRST}"
    return ws


# ----------------------------------------------------------------------------
# P&L Yn: one column per contract row plus a Year total column
# ----------------------------------------------------------------------------
PL_ROWS = [
    ("Contract revenue", "H", USD),
    ("Less raw materials used", "I", USD),
    ("Less production wages", "J", USD),
    ("Less other direct contract expenses", "K", USD),
    ("Contribution margin", None, USD),
    ("Less fixed operating expenses", None, USD),
    ("Operating profit", None, USD),
    ("CM %", None, PCT),
    ("Operating margin %", None, PCT),
    ("Share of market (revenue / market size)", None, PCT),
]
PL_FIRST = 6  # first P&L line
PL = {label: PL_FIRST + i for i, (label, _, _) in enumerate(PL_ROWS)}
R_REV, R_RM, R_WAGE, R_OTH = (PL[l] for l in [r[0] for r in PL_ROWS[:4]])
R_CM, R_FX, R_OP = PL["Contribution margin"], PL["Less fixed operating expenses"], PL["Operating profit"]
R_CMP, R_OMP, R_SHARE = PL["CM %"], PL["Operating margin %"], PL["Share of market (revenue / market size)"]


def build_pl(year):
    ws = wb.create_sheet(f"P&L Y{year}")
    ws.sheet_properties.tabColor = "ED7D31"
    cs = f"'Contracts Y{year}'"
    mkt = MARKET[year]
    put(ws, "A1", f"Year {year} profit and loss", font=F_TITLE)
    put(ws, "A2", f"Contract columns read {cs.strip(chr(39))} row by row; blank columns are unused "
                  "contract rows. Year total sums the whole contract range. Costs shown as positive "
                  "amounts that are subtracted.", font=F_NOTE)

    put(ws, "A4", "Contract", font=F_HEAD, fill=FILL_HEAD, align=WRAP_CENTER)
    put(ws, "A5", "Spec", font=F_HEAD, fill=FILL_HEAD, align=WRAP_CENTER)
    put(ws, "B4", "Year total", font=F_HEAD, fill=FILL_HEAD, align=WRAP_CENTER)
    put(ws, "B5", "", font=F_HEAD, fill=FILL_HEAD)

    for label, _, fmt in PL_ROWS:
        bold = label in ("Contribution margin", "Operating profit")
        put(ws, f"A{PL[label]}", label, font=F_BOLD if bold else F_BASE)

    # Year total column (B): SUM over the whole contract range on the Contracts sheet
    def rng(col):
        return f"{cs}!{col}${FIRST}:{col}${LAST}"

    put(ws, f"B{R_REV}", f"=SUM({rng('H')})", font=F_LINK, fmt=USD)
    put(ws, f"B{R_RM}", f"=SUM({rng('I')})", font=F_LINK, fmt=USD)
    put(ws, f"B{R_WAGE}", f"=SUM({rng('J')})", font=F_LINK, fmt=USD)
    put(ws, f"B{R_OTH}", f"=SUM({rng('K')})", font=F_LINK, fmt=USD)
    put(ws, f"B{R_CM}", f"=B{R_REV}-B{R_RM}-B{R_WAGE}-B{R_OTH}", font=F_BOLD, fmt=USD,
        border=TOP_LINE)
    put(ws, f"B{R_FX}", "=FixedTotal", font=F_LINK, fmt=USD)
    put(ws, f"B{R_OP}", f"=B{R_CM}-B{R_FX}", font=F_BOLD, fmt=USD, border=TOP_LINE)
    put(ws, f"B{R_CMP}", f'=IF(B{R_REV}=0,"",B{R_CM}/B{R_REV})', fmt=PCT)
    put(ws, f"B{R_OMP}", f'=IF(B{R_REV}=0,"",B{R_OP}/B{R_REV})', fmt=PCT)
    put(ws, f"B{R_SHARE}", f'=IF(N({mkt})=0,"",B{R_REV}/{mkt})', fmt=PCT)

    # One column per contract row
    for i in range(N_ROWS):
        c = get_column_letter(3 + i)
        r = FIRST + i
        blank = f'IF({c}$4="",""'
        put(ws, f"{c}4", f'=IF({cs}!$A{r}="","",{cs}!$A{r})', font=F_HEAD, fill=FILL_HEAD,
            align=WRAP_CENTER)
        put(ws, f"{c}5", f'=IF({cs}!$A{r}="","",{cs}!$B{r})', font=F_HEAD, fill=FILL_HEAD,
            align=WRAP_CENTER)
        for row, src in ((R_REV, "H"), (R_RM, "I"), (R_WAGE, "J")):
            put(ws, f"{c}{row}", f"={blank},{cs}!{src}{r})", font=F_LINK, fmt=USD)
        put(ws, f"{c}{R_OTH}", f"={blank},N({cs}!K{r}))", font=F_LINK, fmt=USD)
        put(ws, f"{c}{R_CM}", f"={blank},{c}{R_REV}-{c}{R_RM}-{c}{R_WAGE}-{c}{R_OTH})",
            font=F_BOLD, fmt=USD, border=TOP_LINE)
        style(ws[f"{c}{R_FX}"], fmt=USD)
        style(ws[f"{c}{R_OP}"], fmt=USD, border=TOP_LINE)
        put(ws, f"{c}{R_CMP}", f'=IF(N({c}{R_REV})=0,"",{c}{R_CM}/{c}{R_REV})', fmt=PCT)
        style(ws[f"{c}{R_OMP}"], fmt=PCT)
        put(ws, f"{c}{R_SHARE}", f'=IF(OR({c}$4="",N({mkt})=0),"",{c}{R_REV}/{mkt})', fmt=PCT)
        ws.column_dimensions[c].width = 12

    put(ws, f"A{R_SHARE + 2}", "Fixed expenses, operating profit and operating margin are "
                              "reported for the year only, not per contract.", font=F_NOTE)
    ws.column_dimensions["A"].width = 40
    ws.column_dimensions["B"].width = 14
    ws.freeze_panes = "C6"
    return ws


for year in (1, 2, 3):
    build_contracts(year, Y1_CONTRACTS if year == 1 else [])
    build_pl(year)

# C09 quantity was crossed out on the contract card: flag it.
c09_row = FIRST + [c[0] for c in Y1_CONTRACTS].index("C09")
c09 = wb["Contracts Y1"][f"C{c09_row}"]
c09.fill = FILL_CONFIRM
c09.comment = Comment("Confirm quantity", "Budget model")

# Put sheets in reading order: Inputs, Y1, Y2, Y3, then Summary
order = ["Inputs", "Contracts Y1", "P&L Y1", "Contracts Y2", "P&L Y2", "Contracts Y3", "P&L Y3"]
wb._sheets = [wb[n] for n in order]

# ----------------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------------
ws = wb.create_sheet("Summary", 1)
ws.sheet_properties.tabColor = "C00000"
put(ws, "A1", "Three-year summary", font=F_TITLE)
put(ws, "A2", "Links to the Year total column of each P&L sheet. Years 2 and 3 fill in as "
              "contracts are typed into Contracts Y2 / Y3.", font=F_NOTE)
header_row(ws, 4, ["($)", "Year 1", "Year 2", "Year 3"])
S_ROWS = [
    ("Revenue", R_REV, USD, F_LINK),
    ("Contribution margin", R_CM, USD, F_LINK_BOLD),
    ("Fixed operating expenses", R_FX, USD, F_LINK),
    ("Operating profit", R_OP, USD, F_LINK_BOLD),
    ("CM %", None, PCT, F_BASE),
    ("Operating margin %", None, PCT, F_BASE),
    ("Cumulative operating profit", None, USD, F_BOLD),
    ("Market size", None, USD, F_LINK),
    ("Share of market", R_SHARE, PCT, F_LINK),
]
for i, (label, _, _, _) in enumerate(S_ROWS, start=5):
    put(ws, f"A{i}", label, font=F_BOLD if "profit" in label.lower() or label ==
        "Contribution margin" else F_BASE)
for y, col in zip((1, 2, 3), "BCD"):
    pl = f"'P&L Y{y}'"
    put(ws, f"{col}5", f"={pl}!$B${R_REV}", font=F_LINK, fmt=USD)
    put(ws, f"{col}6", f"={pl}!$B${R_CM}", font=F_LINK_BOLD, fmt=USD)
    put(ws, f"{col}7", f"={pl}!$B${R_FX}", font=F_LINK, fmt=USD)
    put(ws, f"{col}8", f"={pl}!$B${R_OP}", font=F_LINK_BOLD, fmt=USD, border=TOP_LINE)
    put(ws, f"{col}9", f'=IF({col}5=0,"",{col}6/{col}5)', fmt=PCT)
    put(ws, f"{col}10", f'=IF({col}5=0,"",{col}8/{col}5)', fmt=PCT)
    put(ws, f"{col}11", f"=SUM($B8:{col}8)", font=F_BOLD, fmt=USD, fill=FILL_TOTAL)
    put(ws, f"{col}12", f"={MARKET[y]}", font=F_LINK, fmt=USD)
    put(ws, f"{col}13", f"={pl}!$B${R_SHARE}", font=F_LINK, fmt=PCT)
put(ws, "A15", "Fixed operating expenses are charged every year, so a year with no contracts "
               "entered still shows an operating loss equal to fixed expenses.", font=F_NOTE)
ws.column_dimensions["A"].width = 32
for col in "BCD":
    ws.column_dimensions[col].width = 15
ws.freeze_panes = "B5"

wb.calculation = CalcProperties(fullCalcOnLoad=True)
wb.active = 0
wb.save(OUT)
print(f"Wrote {OUT}")
