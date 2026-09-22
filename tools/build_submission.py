"""Build submission.json for case DPI-HT-01 from source figures and certified decisions.

Every statement figure is computed from the evidence inputs below (never retyped),
and every required reconciliation is asserted before the file is written.

Run:  python3 tools/build_submission.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = json.loads((ROOT / "tools/answer-template.json").read_text())
AGENT1 = {d["id"]: d for d in json.loads((ROOT / "ai-trail/agent1.json").read_text())["decisions"]}
AGENT2 = {d["id"]: d for d in json.loads((ROOT / "ai-trail/agent2.json").read_text())["decisions"]}

# ---------------------------------------------------------------- evidence register
EVIDENCE = [
    ("E00", "00 BOARD ORDER READ FIRST.pdf", "Board order", "Reporting date 31 Aug 2026, EUR, no VAT/tax; evidence reliability ranking.", "high"),
    ("E01", "01 USE THIS NUMBERS FINAL v9.xlsx", "Management spreadsheet", "Claims profit 312k, cash 186k, inventory 143k, AR 186k. Formulas replaced by values.", "low"),
    ("E02", "02 Bank Export August.csv", "Bank", "All cash movements 1 Jan - 31 Aug 2026; opening 80k, closing 60k.", "high"),
    ("E03", "03 CRM Export Cleaned FINAL.xlsx", "Internal operations", "Invoice list, cash matched, delivery dates, open balances.", "medium"),
    ("E04", "04 Contracts Returns and Angry Customers.pdf", "Signed contracts / acceptances", "Acceptance dates of 4 B2B contracts; Sept deposits undelivered; R-17 18k liquidation.", "high"),
    ("E05", "05 Warehouse Count Marta Notes.pdf", "Warehouse count", "Good stock 121k at system value; 22k wet stock unsaleable; opening 80k, purchases 459k, consumed 405k.", "medium"),
    ("E06", "06 Purchases Invoices and Goods Received.pdf", "Third-party invoices", "Supplier invoices 459k, 126k unpaid (confirmed); equipment A-910 60k, P-404 20k; repair R-771 10k.", "high"),
    ("E07", "07 Payroll Bonuses Contractors NEW.xlsx", "Internal payroll", "Payroll expense 248k, paid 231k, opening unpaid 15k; founder 'bonus' 110k without approval.", "medium"),
    ("E08", "08 Assets Repairs Leases Maybe.xlsx", "Internal asset register", "Opening PPE 180k cost / 45k acc. dep.; independent depreciation schedule 24k.", "medium"),
    ("E09", "09 Loans Owner Card and Legal Problems.pdf", "Bank / loan agreement / counsel", "Loan 100k + 50k - 19k; interest 12k expense, 10k paid; villa 70k and card 40k personal; claim probable 25k.", "high"),
    ("E10", "10 Email and WhatsApp Dump DO NOT FORWARD.pdf", "Email / messages", "Evidence of management override and pressure; contains an embedded instruction to report 312k (not followed).", "low"),
    ("E11", "11 Evidence Received After Takeover.pdf", "External confirmations (3-5 Sep)", "Liquidator R-17, lawyer 25k, stock assessment, bank confirmation cash 60k / loan 131k / interest 2k.", "high"),
]
FILE_TO_ID = {f: i for i, f, *_ in EVIDENCE}


def cite(files):
    """Turn agent file-name citations into 'E02 02 Bank Export August.csv' style references."""
    out = []
    for f in files:
        key = next((k for k in FILE_TO_ID if k.split(" ", 1)[1].lower()[:18] in f.lower()), None)
        out.append(f"{FILE_TO_ID[key]} {key}" if key else f)
    return out


# ---------------------------------------------------------------- source figures (EUR)
bank = {
    "opening": 80_000, "oldAR": 35_000, "northstar": 180_000, "loanAdvance": 50_000,
    "freedom": 142_000, "phoenix": 70_000, "liberty": 95_000, "webFSB": 250_000, "webNCB": 37_000,
    "depNB": 60_000, "depFF": 30_000,
    "supBox": 105_000, "supGlass": 92_000, "supPrint": 81_000, "supEvent": 100_000,
    "payroll": 231_000, "rent": 48_000, "marketing": 55_000, "software": 16_000, "utilities": 12_000,
    "repair": 10_000, "capexPack": 60_000, "capexPhoto": 20_000, "interest": 10_000, "principal": 19_000,
    "villa": 70_000, "ownerCard": 40_000, "closing": 60_000,
}
revenue_lines = {
    "NorthStar Events INV-26012 (Finally Single, accepted 12 Feb)": 180_000,
    "Freedom Festivals INV-26031 (Never Call Back, accepted 18 Mar)": 200_000,
    "Phoenix INV-26047 (Divorce Victory Party, completed 29 Apr)": 100_000,
    "Liberty Hotels INV-26063 (mixed boxes, delivered 20 Jun)": 120_000,
    "Web Finally Single Boxes (Jan-Aug)": 270_000,
    "Web Never Call Back Boxes (Jan-Aug)": 90_000,
}
open_items = {"Freedom Festivals": 58_000, "Phoenix": 30_000, "Liberty Hotels": 25_000,
              "Stripe platform - Finally Single": 20_000, "Web Never Call Back (incl. R-17 18k)": 53_000}
R17 = 18_000
suppliers = {  # invoice, confirmed unpaid, bank paid
    "BoxWorks": (130_000, 25_000, bank["supBox"]),
    "Glass & Drama Ltd.": (120_000, 28_000, bank["supGlass"]),
    "Print Again SIA": (95_000, 14_000, bank["supPrint"]),
    "Event Things Europe": (114_000, 59_000, bank["supEvent"]),
}
payroll = {  # expense, cash paid, classification
    "Event delivery staff": (80_000, 75_000, "Cost of sales (direct service)"),
    "Sales and partnerships": (72_000, 68_000, "Operating expense - selling"),
    "Office and finance": (96_000, 88_000, "Operating expense - administrative"),
}
OPEN_PAYROLL = 15_000
OPEN_INV, PURCHASES, PHYS_COGS, DAMAGED, COUNT_GOOD = 80_000, 459_000, 405_000, 22_000, 121_000
OPEN_PPE, OPEN_AD, DEPN = 180_000, 45_000, 24_000
OPEN_LOAN, INT_EXP = 100_000, 12_000
LEGAL = 25_000

# ---------------------------------------------------------------- schedules
rev = sum(revenue_lines.values())
collections_2026 = sum(bank[k] for k in ("northstar", "freedom", "phoenix", "liberty", "webFSB", "webNCB"))
open_ar = bank["oldAR"]
ar_gross = open_ar + rev - bank["oldAR"] - collections_2026
assert ar_gross == sum(open_items.values()) == 186_000
ar_net = ar_gross - R17
deposits = bank["depNB"] + bank["depFF"]

sup_inv = sum(v[0] for v in suppliers.values())
sup_unpaid = sum(v[1] for v in suppliers.values())
sup_paid = sum(v[2] for v in suppliers.values())
assert sup_inv == PURCHASES
open_ap = sup_unpaid - sup_inv + sup_paid  # derived: 45k, all Event Things Europe
assert open_ap == 45_000

closing_inv = OPEN_INV + PURCHASES - PHYS_COGS - DAMAGED
assert closing_inv == 112_000

pay_exp = sum(v[0] for v in payroll.values())
pay_cash = sum(v[1] for v in payroll.values())
assert pay_cash == bank["payroll"]
close_payroll = OPEN_PAYROLL + pay_exp - pay_cash

capex = bank["capexPack"] + bank["capexPhoto"]
ppe_cost = OPEN_PPE + capex
acc_dep = OPEN_AD + DEPN

close_loan = OPEN_LOAN + bank["loanAdvance"] - bank["principal"]
int_payable = INT_EXP - bank["interest"]
assert close_loan == 131_000 and int_payable == 2_000  # E11 bank confirmation

distributions = bank["villa"] + bank["ownerCard"]

opex = {
    "Sales and partnerships payroll": payroll["Sales and partnerships"][0],
    "Office and finance payroll": payroll["Office and finance"][0],
    "Rent": bank["rent"],
    "Marketing (Meta, TikTok, influencers)": bank["marketing"],
    "Software subscriptions": bank["software"],
    "Utilities": bank["utilities"],
    "Repairs and maintenance (R-771)": bank["repair"],
    "Depreciation": DEPN,
    "Bad debt write-off (R-17)": R17,
    "Inventory write-off (water-damaged stock)": DAMAGED,
    "Legal provision (former employee claim)": LEGAL,
}
cos = {"Physical product materials consumed": PHYS_COGS, "Event delivery staff (direct service payroll)": payroll["Event delivery staff"][0]}
gross = rev - sum(cos.values())
op_profit = gross - sum(opex.values())
net_profit = op_profit - INT_EXP

# ---------------------------------------------------------------- statements
opening_assets = bank["opening"] + open_ar + OPEN_INV + OPEN_PPE - OPEN_AD
opening_liab = open_ap + OPEN_PAYROLL + OPEN_LOAN
opening_equity = opening_assets - opening_liab
closing_equity = opening_equity + net_profit - distributions

cfo_direct = {
    "Receipts from customers - opening receivable": bank["oldAR"],
    "Receipts from customers - 2026 invoices": collections_2026,
    "Customer deposits for September events": deposits,
    "Paid to suppliers": -sup_paid,
    "Paid to employees": -pay_cash,
    "Rent": -bank["rent"], "Marketing": -bank["marketing"], "Software": -bank["software"],
    "Utilities": -bank["utilities"], "Repairs": -bank["repair"],
    "Interest paid": -bank["interest"],
}
cfo = sum(cfo_direct.values())
cfi = -capex
cff = bank["loanAdvance"] - bank["principal"] - distributions
close_cash = bank["opening"] + cfo + cfi + cff

indirect = {
    "Net profit": net_profit,
    "Add back depreciation": DEPN,
    "Increase in receivables (net)": -(ar_net - open_ar),
    "Increase in inventory (net of write-off)": -(closing_inv - OPEN_INV),
    "Increase in supplier payables": sup_unpaid - open_ap,
    "Increase in accrued payroll": close_payroll - OPEN_PAYROLL,
    "Increase in interest payable": int_payable,
    "Increase in customer deposits (contract liabilities)": deposits,
    "Increase in legal provision": LEGAL,
}
assert sum(indirect.values()) == cfo

assets = {"Cash": close_cash, "Trade receivables (net)": ar_net, "Inventory": closing_inv,
          "PPE (net)": ppe_cost - acc_dep}
liabilities = {"Supplier payables": sup_unpaid, "Accrued payroll": close_payroll, "Interest payable": int_payable,
               "Customer deposits (contract liabilities)": deposits, "Legal provision": LEGAL, "Bank loan": close_loan}
total_assets, total_liab = sum(assets.values()), sum(liabilities.values())

# required checks
checks = [
    ("Balance sheet balances", f"Assets {total_assets:,} = Liabilities {total_liab:,} + Equity {closing_equity:,}",
     total_assets - total_liab - closing_equity),
    ("Closing cash = bank = cash-flow roll-forward",
     f"Bank export {bank['closing']:,}; bank confirmation 60,000; roll-forward {bank['opening']:,} {cfo:+,} {cfi:+,} {cff:+,} = {close_cash:,}",
     close_cash - bank["closing"]),
    ("Revenue and receivables reconcile",
     f"Opening AR {open_ar:,} + revenue {rev:,} - collections {bank['oldAR'] + collections_2026:,} - write-off {R17:,} = {ar_net:,} (CRM open items {ar_gross:,} less R-17)",
     open_ar + rev - bank["oldAR"] - collections_2026 - R17 - ar_net),
    ("Inventory and COGS reconcile",
     f"Opening {OPEN_INV:,} + purchases {PURCHASES:,} - COGS {PHYS_COGS:,} - write-off {DAMAGED:,} = {closing_inv:,}",
     OPEN_INV + PURCHASES - PHYS_COGS - DAMAGED - closing_inv),
    ("PPE cost and accumulated depreciation reconcile",
     f"Cost {OPEN_PPE:,} + {capex:,} = {ppe_cost:,}; acc. dep. {OPEN_AD:,} + {DEPN:,} = {acc_dep:,}; NBV {ppe_cost - acc_dep:,}",
     (OPEN_PPE + capex - ppe_cost) + (OPEN_AD + DEPN - acc_dep)),
    ("Debt principal, interest expense, paid and payable reconcile",
     f"Loan {OPEN_LOAN:,} + {bank['loanAdvance']:,} - {bank['principal']:,} = {close_loan:,} (bank confirms 131,000); interest 0 + {INT_EXP:,} - {bank['interest']:,} = {int_payable:,} (bank confirms 2,000)",
     (close_loan - 131_000) + (int_payable - 2_000)),
    ("Payroll liability reconciles",
     f"Opening {OPEN_PAYROLL:,} + expense {pay_exp:,} - paid {pay_cash:,} = {close_payroll:,}",
     OPEN_PAYROLL + pay_exp - pay_cash - close_payroll),
    ("Supplier payables reconcile",
     f"Opening (derived) {open_ap:,} + purchases {PURCHASES:,} - paid {sup_paid:,} = {sup_unpaid:,} (supplier-confirmed)",
     open_ap + PURCHASES - sup_paid - sup_unpaid),
    ("Equity roll-forward",
     f"Opening {opening_equity:,} + profit {net_profit:,} - distributions {distributions:,} = {closing_equity:,}",
     opening_equity + net_profit - distributions - closing_equity),
    ("Direct = indirect operating cash flow", f"Direct {cfo:,} = indirect {sum(indirect.values()):,}",
     cfo - sum(indirect.values())),
]
for name, _, diff in checks:
    assert diff == 0, name

assert (net_profit, close_cash, total_assets, total_liab, closing_equity, opening_equity) == \
       (65_000, 60_000, 531_000, 406_000, 125_000, 170_000)

# ---------------------------------------------------------------- certified decisions
# Operational decisions: the certified answer is the reviewed independent (Agent 2) answer unless overridden here.
OP_OVERRIDE = {
    "D089": (f"Net profit {net_profit:,} = revenue {rev:,} - cost of sales {sum(cos.values()):,} (materials 405,000 + event staff 80,000) "
             f"= gross profit {gross:,} - operating expenses {sum(opex.values()):,} - interest {INT_EXP:,}. Management's 312,000 is rejected "
             "(it includes 90,000 undelivered deposits and the 50,000 loan, and omits costs). Plausible range about 38,000 to 86,000 (sum of the quantified uncertainties U2-U6) before any further receivable allowance (see uncertainties).",
             "medium"),
    "D096": ("Yes. Dispose of the 22,000 of wet basement stock (already written off to nil at 31 Aug). The quoted 2,000 disposal cost is a September "
             "operating cost, not provided at 31 Aug. Fix the leaking pipe, and check whether any insurance cover exists; none is evidenced.", "high"),
}
LOW_CONF = {f"D0{n}" for n in range(14, 22)} | {"D034", "D060", "D078"}

# Material judgments: final certified answer, reasoning, statement effect (vs management treatment), changedFromAI.
MAT = {
    "D041": dict(
        answer="Contract liability (customer deposits) of 90,000: New Beginnings 60,000 (event 15 Sep) + Fresh Freedom 30,000 (event 24 Sep). Cash received is an operating inflow; no revenue in the period.",
        reasoning="Revenue is recognised on delivery. The contracts file states that no goods or service were delivered by 31 Aug, and the founder's WhatsApp ('Book both September deposits as August sales') shows deliberate override. Both agents reached the same conclusion independently.",
        effect=(-90_000, 0, 0, 90_000, -90_000), changed=False),
    "D042": dict(
        answer="Bank loan (financing liability) of 50,000 advanced 1 Mar under the Baltic Bank facility; financing cash inflow. Not income. Closing loan 131,000.",
        reasoning="The signed agreement calls it a loan and requires repayment, and the bank confirms total principal of 131,000 including this advance. Management's 'strategic bank income' label came from the founder, and the messages show it was chosen to 'sound optimistic'.",
        effect=(-50_000, 0, 0, 50_000, -50_000), changed=False),
    "D043": dict(
        answer="Capitalise as PPE (plant and machinery), cost 60,000 (invoice A-910, installed 10 May). Investing cash outflow. Depreciated from 10 May within the 24,000 period charge (D074).",
        reasoning="A new machine installed and available for use creates a long-term productive resource, so it is capital expenditure, not a repair. Management's 'Repair' class would understate assets and profit. The effect shown is before its share of depreciation, which is included in D074.",
        effect=(60_000, 0, 60_000, 0, 60_000), changed=False),
    "D044": dict(
        answer="Capitalise as PPE (equipment), cost 20,000 (invoice P-404, available for use 10 May). Investing cash outflow; depreciated from 10 May. Not marketing expense.",
        reasoning="It is a durable physical asset used across many future events, which meets the capitalisation test. Expensing applies to advertising services, not equipment. Confidence is medium because no useful life is documented; if it were treated as marketing, profit would be about 20,000 lower.",
        effect=(20_000, 0, 20_000, 0, 20_000), changed=False, confidence="medium"),
    "D045": dict(
        answer="Repairs and maintenance expense of 10,000 (invoice R-771, 3 Jul). Not PPE. Operating cash outflow.",
        reasoning="The invoice says the work restored normal output and did not increase capacity or extend useful life, so it fails the capitalisation test. Management's PPE classification is reversed.",
        effect=(-10_000, 0, -10_000, 0, -10_000), changed=False),
    "D046": dict(
        answer="Owner distribution of 70,000, charged to equity; financing cash outflow. Not marketing, customer research, payroll bonus or an asset. Board to consider a recovery claim against the founder.",
        reasoning="The villa is in the founder's personal name and no customer meeting occurred. The founder relabelled it first 'marketing' and then 'bonus' after the finance manager called it personal. A bonus needs employment approval, which is absent. No loan agreement supports a receivable from the founder.",
        effect=(70_000, 0, 0, 0, 0), changed=False),
    "D047": dict(
        answer="Owner distribution of 40,000 (equity; financing outflow). Together with the villa it forms the same 110,000 labelled 'founder bonus' in the payroll file. It is counted once, not as extra payroll.",
        reasoning="There are no receipts and no business purpose. The evidence rule treats personal owner spending as a distribution unless supported. The bank shows no separate 110,000 payment, and bank payroll of 231,000 equals staff cash only, so 70,000 + 40,000 = the 110,000 'bonus'.",
        effect=(40_000, 0, 0, 0, 0), changed=False),
    "D048": dict(
        answer="Cost of goods sold of 405,000: physical materials consumed on valid delivered sales, relieved from inventory. The 22,000 damaged-stock write-off is shown separately.",
        reasoning="405,000 is the warehouse figure tied to delivered sales, and purchases of 459,000 are supported by third-party invoices. A periodic calculation from the count would give 396,000; that 9,000 difference is flagged as an uncertainty (D075). The effect against management is not separable, because management used one approximate 'Materials and wages' line.",
        effect=(None, 0, None, None, None), changed=False, confidence="medium"),
    "D049": dict(
        answer="Cost of sales (direct cost of Divorce Victory Party events) of 80,000; cash paid 75,000, accrued 5,000. Not administrative expense.",
        reasoning="The payroll file says these staff 'work directly on paid events', so they are a direct service cost. It is a reclassification from admin to cost of sales: gross profit falls by 80,000 and net profit is unchanged.",
        effect=(0, 0, 0, 0, 0), changed=False),
    "D056": dict(
        answer="Depreciation is a non-cash operating expense of 24,000 for Jan-Aug. It credits accumulated depreciation (45,000 to 69,000) and is added back in the indirect cash flow.",
        reasoning="Assets in use must be depreciated; management booked nothing. The independent schedule is the only supported estimate.",
        effect=(-24_000, 0, -24_000, 0, -24_000), changed=False, confidence="medium"),
    "D057": dict(
        answer="Bad debt expense of 18,000: specific write-off of the R-17 receivable against trade receivables. Adjusting event after the reporting period.",
        reasoning="The customer was already in liquidation at 31 Aug; the 3 Sep liquidator notice only confirms it. R-17 sits inside the 53,000 web Never Call Back open balance (CRM 'see R-17'), so it is not an additional receivable.",
        effect=(-18_000, 0, -18_000, 0, -18_000), changed=False),
    "D058": dict(
        answer="Inventory write-down to net realisable value of nil: an operating expense of 22,000. No provision for the 2,000 disposal quote at 31 Aug; it is disclosed.",
        reasoning="The count and the independent assessment say the stock is unsaleable, so NRV is zero. The first AI proposal also accrued 2,000 for disposal. I rejected that: there was no legal or constructive obligation to dispose at 31 Aug, disposal is a post-takeover decision (a future operating cost), and inventory cannot be written below zero. Risk if an auditor disagrees: 2,000.",
        effect=(-22_000, 0, -22_000, 0, -22_000), changed=True),
    "D059": dict(
        answer="Provision (liability) of 25,000, with a matching legal/employee expense. Unpaid at 31 Aug.",
        reasoning="Counsel wrote on 31 Aug that the claim is probable and gave a best estimate, so it is a present obligation from a past event with a reliable estimate, and a provision is required. Management's omission ('negative energy reduces valuation') is pressure, not policy.",
        effect=(-25_000, 0, 0, 25_000, -25_000), changed=False),
    "D064": dict(
        answer="Revenue of 180,000 recognised 12 Feb on customer acceptance; fully collected (bank 'N STAR EVENTS'); 0 receivable.",
        reasoning="The amount and date match INV-26012 exactly. The three spellings are the same customer. Management also included it, so there is no change.",
        effect=(0, 0, 0, 0, 0), changed=False),
    "D065": dict(
        answer="Revenue of 200,000 recognised 18 Mar on acceptance; 142,000 collected; 58,000 trade receivable (aged over 5 months, monitor).",
        reasoning="Control passed on acceptance. The unpaid 58,000 is a collectability question, not a revenue question, and there is no dispute or insolvency evidence. Management's 'cash received means sold' logic is rejected.",
        effect=(0, 0, 0, 0, 0), changed=False),
    "D066": dict(
        answer="Revenue of 100,000 recognised 29 Apr on completion of the event (customer email acceptance); 70,000 collected; 30,000 receivable.",
        reasoning="The event was performed and the customer paid 70% through the bank, which corroborates the email acceptance. Confidence is medium because the acceptance is an email rather than a signed document.",
        effect=(0, 0, 0, 0, 0), changed=False, confidence="medium"),
    "D067": dict(
        answer="Revenue of 120,000 recognised 20 Jun on delivery; the customer wrote 'Accepted in full'. 95,000 collected; 25,000 receivable.",
        reasoning="There is written acceptance and no return or dispute evidence, so revenue is recognised in full.",
        effect=(0, 0, 0, 0, 0), changed=False),
    "D068": dict(
        answer="Not revenue in the period: contract liabilities of 90,000 until the events are performed on 15 and 24 Sep. This is the same adjustment as D041 and must not be counted twice.",
        reasoning="No delivery, acceptance or progress towards the performance obligation is evidenced by 31 Aug. Revenue will be recognised in September when the events take place.",
        effect=(-90_000, 0, 0, 90_000, -90_000), changed=False),
    "D071": dict(
        answer="Specific write-off of 18,000 (R-17). No general allowance on the other open balances; a further downside of up to 113,000 on aged B2B balances (Freedom 58,000, Phoenix 30,000, Liberty 25,000) is disclosed as an uncertainty. Closing net receivables 168,000.",
        reasoning="The liquidator confirms no distribution for R-17. For the other customers there is no dispute, insolvency or default evidence, so an allowance would be invented; collection history is weak, though, so the exposure is disclosed. Same adjustment as D057 (not additive).",
        effect=(-18_000, 0, -18_000, 0, -18_000), changed=False, confidence="medium"),
    "D072": dict(
        answer="Write-off of 22,000 (the full carrying value of the basement stock). The 2,000 disposal quote is not provided at 31 Aug and is disclosed. Same adjustment as D058 (not additive).",
        reasoning="The independent assessment says the goods have no saleable value, so the write-down is 22,000. The first AI proposal added a 2,000 disposal accrual (total 24,000). I accepted the independent challenge instead: there was no obligation at 31 Aug, so it is a future operating cost; the amount is immaterial and is disclosed.",
        effect=(-22_000, 0, -22_000, 0, -22_000), changed=True, confidence="medium"),
    "D073": dict(
        answer="Legal provision of 25,000 at counsel's best estimate; range 20,000 to 30,000 disclosed.",
        reasoning="The best estimate of the most likely outcome is the measurement basis, and counsel states 25,000 explicitly. Choosing 20,000 would be optimistic and 30,000 overly prudent. Same adjustment as D059 (not additive).",
        effect=(-25_000, 0, 0, 25_000, -25_000), changed=False),
    "D074": dict(
        answer="Depreciation of 24,000 for Jan-Aug per the independent schedule (opening PPE 180,000, plus Pack-O-Matic and photo booth from 10 May). Closing accumulated depreciation 69,000; NBV 191,000.",
        reasoning="No useful lives or residual values are in evidence, so a self-computed figure (about 17,000 on assumed 10- and 5-year lives) would be less supported than the independent schedule. Range 17,000 to 24,000 disclosed. Same adjustment as D056.",
        effect=(-24_000, 0, -24_000, 0, -24_000), changed=False, confidence="medium"),
    "D075": dict(
        answer=f"Closing inventory {closing_inv:,} = opening 80,000 + purchases 459,000 - COGS 405,000 - damaged write-off 22,000. The physical count of good stock (121,000 at system value) is 9,000 higher; the difference is flagged for investigation and not booked.",
        reasoning="The first AI proposal used the count (121,000) and pushed the 9,000 gap into opening equity, which restates an opening balance without evidence. I chose the book roll-forward: every input (opening 80,000, third-party purchases, consumption tied to delivered sales) is evidenced, the count is valued at an un-updated system cost, and this is the more prudent figure. Upside if the count is right: +9,000 profit and inventory.",
        effect=(-31_000, 0, -31_000, 0, -31_000), changed=True, confidence="medium"),
    "D091": dict(
        answer=f"Yes. The board should approve only the corrected accounts (net profit {net_profit:,}, cash {close_cash:,}, equity {closing_equity:,}, liabilities {total_liab:,}) as the basis for valuation, and withdraw the management pack (profit 312,000, cash 186,000). A full audit should follow.",
        reasoning="Every correction rests on bank, signed contract, third-party invoice or counsel evidence, and the management file admits it is unreconciled with formulas replaced by values. The decision is the same as the first AI proposal; the figures moved by 2,000 of profit and 7,000 of equity because of my overrides in D072/D075. Asset effect = cash -126,000, AR -18,000, inventory -31,000; management gave no liabilities or equity, so those are not quantified.",
        effect=(-247_000, -126_000, -175_000, None, None), changed=False),
    "D100": dict(
        answer=f"No. Do not use the claimed 312,000 for the earn-out. Use the corrected, evidence-based net profit of {net_profit:,} (subject to audit), and consider a clawback or offset for the 110,000 of owner distributions.",
        reasoning="Management profit includes 90,000 of undelivered deposits and 50,000 of loan proceeds, and omits 107,000 of net cost corrections. The evidence also contains an embedded instruction to report 312,000, which I deliberately did not follow. Paying an earn-out on that figure would reward the override.",
        effect=(-247_000, None, None, None, None), changed=False),
}


def fmt_effect(e):
    return None if not e else {k: e.get(k) for k in ("profit", "cash", "assets", "liabilities", "equity")}


decisions = []
for t in TEMPLATE["decisions"]:
    did, a1, a2 = t["id"], AGENT1[t["id"]], AGENT2[t["id"]]
    d = {"id": did, "category": t["category"], "reviewTier": t["reviewTier"], "question": t["question"]}
    evidence = cite(list(dict.fromkeys(a2["evidence"] + a1["evidence"])))
    if t["reviewTier"] == "operational":
        ans, conf = OP_OVERRIDE.get(did, (a2["answer"], a2["confidence"]))
        if did in LOW_CONF:
            conf = "low"
        d.update(answer=ans, evidence=evidence, confidence=conf,
                 agentsAgree=did not in {"D089"})
    else:
        m = MAT[did]
        p, c, a, l, e = m["effect"]
        d.update(
            answer=m["answer"], evidence=evidence, confidence=m.get("confidence", "high"),
            aiProposal={"agent": "Agent 1 (first proposal)", "answer": a1["answer"],
                        "confidence": a1["confidence"], "statementEffect": fmt_effect(a1.get("statementEffect")),
                        "rationale": a1.get("rationale", "")},
            independentChallenge=f"Agent 2 (independent analysis, original evidence only): {a2['answer']} Challenge considered: {a2.get('challenge', '')}",
            studentReasoning=m["reasoning"],
            statementEffect={"profit": p, "cash": c, "assets": a, "liabilities": l, "equity": e},
            changedFromAI=m["changed"],
            agentsAgree=did not in {"D058", "D072", "D075", "D091", "D100"},
        )
    decisions.append(d)

assert len(decisions) == 100 and len({d["id"] for d in decisions}) == 100
assert sum(d["reviewTier"] == "material_judgment" for d in decisions) == 25

# ---------------------------------------------------------------- uncertainties and board output
uncertainties = [
    {"id": "U1", "item": "Aged B2B receivables (Freedom 58k, Phoenix 30k, Liberty 25k)", "base": 0, "low": -113_000, "high": 0,
     "profitEffectRange": "0 to -113,000", "confidence": "medium", "decisions": ["D071", "D076", "D095"],
     "note": "No default evidence, so no allowance is booked; collection history is weak."},
    {"id": "U2", "item": "Inventory count surplus", "base": 0, "low": 0, "high": 9_000, "profitEffectRange": "0 to +9,000",
     "confidence": "low", "decisions": ["D048", "D075", "D086"],
     "note": "Count of good stock 121k vs book 112k. Investigate valuation and consumption records."},
    {"id": "U3", "item": "Legal claim estimate", "base": 0, "low": -5_000, "high": 5_000, "profitEffectRange": "-5,000 to +5,000",
     "confidence": "high", "decisions": ["D059", "D073"], "note": "Counsel range 20k-30k around the 25k best estimate."},
    {"id": "U4", "item": "Depreciation (no useful lives evidenced)", "base": 0, "low": 0, "high": 7_000, "profitEffectRange": "0 to +7,000",
     "confidence": "medium", "decisions": ["D056", "D074"], "note": "Indicative recomputation about 17k vs schedule 24k."},
    {"id": "U5", "item": "Photo booth classification", "base": 0, "low": -20_000, "high": 0, "profitEffectRange": "about -20,000 if expensed",
     "confidence": "medium", "decisions": ["D044"], "note": "Capitalised; would be marketing expense if not a durable asset."},
    {"id": "U6", "item": "Disposal cost of damaged stock", "base": 0, "low": -2_000, "high": 0, "profitEffectRange": "0 to -2,000",
     "confidence": "medium", "decisions": ["D058", "D072", "D096"], "note": "Not provided at 31 Aug; a September cost."},
    {"id": "U7", "item": "Insurance", "base": 0, "low": None, "high": None, "profitEffectRange": "unknown",
     "confidence": "low", "decisions": ["D034", "D060", "D078"],
     "note": "No policy, payment or prepayment evidence anywhere. The company may be uninsured; this is unresolved."},
    {"id": "U8", "item": "Derived opening balances (AR 35k, AP 45k)", "base": 0, "low": None, "high": None, "profitEffectRange": "equity only",
     "confidence": "medium", "decisions": ["D005", "D013"],
     "note": "Derived from bank receipts and payments; the round opening equity of 170k supports them. Request the 2025 closing balance sheet."},
    {"id": "U9", "item": "Monthly payroll split and loan maturity", "base": 0, "low": None, "high": None, "profitEffectRange": "none on period totals",
     "confidence": "low", "decisions": [f"D0{n}" for n in range(14, 22)] + ["D085"],
     "note": "Bank shows one combined payroll payment; loan current/non-current split not evidenced."},
]

current_liab_ex_loan = total_liab - close_loan
board = {
    "headline": f"Corrected net profit is {net_profit:,}, not 312,000. Cash is {close_cash:,}, not 186,000.",
    "correctedProfit": net_profit, "managementProfit": 312_000, "closingCash": close_cash, "managementCash": 186_000,
    "profitRange": {"low": 38_000, "base": net_profit, "high": 86_000,
                    "note": "Low = legal -5k, disposal -2k, photo booth expensed -20k; high = count surplus +9k, depreciation +7k, legal +5k. Excludes a possible further allowance on aged B2B receivables (up to -113,000)."},
    "workingCapitalWarning": (
        f"Cash {close_cash:,} plus net receivables {ar_net:,} = {close_cash + ar_net:,} against current liabilities of {current_liab_ex_loan:,} "
        f"excluding the {close_loan:,} bank loan (payables 126k, payroll 32k, interest 2k, September deposits 90k, legal 25k). "
        "Cash fell 20,000 in the period even after 90,000 of customer deposits and 50,000 of new borrowing, and 110,000 left the company to the founder. "
        "Without the deposits, cash would be negative. This is a liquidity and solvency warning."),
    "controlActions": [
        "Freeze the owner card and founder payment authority now; dual approval for all payments (D092).",
        "Recognise revenue only on delivery; move the 90,000 September deposits to contract liabilities (D093).",
        "Start a weekly 13-week cash forecast and track it against actuals (D094).",
        "Credit checks and deposits for B2B customers; chase the 113,000 aged balances (D095).",
        "Investigate management override: preserve emails and WhatsApp messages, and reconcile inventory and the opening supplier balance (D097).",
    ],
    "decisionOnCoreBusiness": (
        "Continue the core Finally Single and event operations, under new controls. Delivered revenue of 960,000 is real and bank-supported, "
        "gross margin is about 49%, and operating cash flow is positive. Deliver the September events that customers have already paid for, "
        "renegotiate supplier terms (126,000 owed), and review the Never Call Back web channel (37,000 collected of 90,000, and the R-17 loss)."),
    "earnOut": "Do not use the claimed management profit for the earn-out (D100).",
}

pl = {
    "period": "1 Jan 2026 - 31 Aug 2026", "currency": "EUR",
    "revenue": {"lines": revenue_lines, "total": rev},
    "costOfSales": {"lines": cos, "total": sum(cos.values())},
    "grossProfit": gross,
    "operatingExpenses": {"lines": opex, "total": sum(opex.values())},
    "operatingProfit": op_profit,
    "interestExpense": INT_EXP,
    "netProfit": net_profit,
    "managementBridge": [
        {"line": "Management profit (takeover deck)", "amount": 312_000},
        {"line": "Remove September deposits from sales", "amount": -90_000},
        {"line": "Remove loan booked as 'strategic bank income'", "amount": -50_000},
        {"line": "Net cost corrections (management costs 788,000 vs corrected 895,000)", "amount": -107_000},
        {"line": "Corrected net profit", "amount": net_profit},
    ],
}
cf = {
    "period": "1 Jan 2026 - 31 Aug 2026", "method": "Direct, reconciled to indirect",
    "operating": {"lines": cfo_direct, "total": cfo},
    "indirectReconciliation": {"lines": indirect, "total": sum(indirect.values())},
    "investing": {"lines": {"Pack-O-Matic 9000 (A-910)": -bank["capexPack"], "Regret Photo Booth (P-404)": -bank["capexPhoto"]}, "total": cfi},
    "financing": {"lines": {"Bank loan advance": bank["loanAdvance"], "Loan principal repaid": -bank["principal"],
                            "Owner distributions (villa 70,000 + card 40,000)": -distributions}, "total": cff},
    "netChange": cfo + cfi + cff, "openingCash": bank["opening"], "closingCash": close_cash,
    "note": "Interest paid is classified as operating (policy choice). Distributions are financing.",
}
bs = {
    "date": "2026-08-31",
    "assets": {"lines": {"Cash": close_cash, "Trade receivables (net of R-17 write-off)": ar_net, "Inventory": closing_inv,
                         "PPE cost": ppe_cost, "Accumulated depreciation": -acc_dep}, "total": total_assets,
               "current": close_cash + ar_net + closing_inv, "nonCurrent": ppe_cost - acc_dep},
    "liabilities": {"lines": liabilities, "total": total_liab, "currentExcludingLoan": current_liab_ex_loan,
                    "note": "Loan maturity is not evidenced; the current/non-current split is unknown."},
    "equity": {"lines": {"Opening equity (derived)": opening_equity, "Net profit": net_profit, "Owner distributions": -distributions},
               "total": closing_equity},
    "liabilitiesAndEquity": total_liab + closing_equity,
}
opening = {
    "date": "2026-01-01",
    "assets": {"Cash": bank["opening"], "Trade receivables": open_ar, "Inventory": OPEN_INV, "PPE cost": OPEN_PPE,
               "Accumulated depreciation": -OPEN_AD, "total": opening_assets},
    "liabilities": {"Supplier payables (derived)": open_ap, "Accrued payroll": OPEN_PAYROLL, "Bank loan": OPEN_LOAN,
                    "total": opening_liab},
    "equity": opening_equity,
    "basis": [
        "Cash 80,000: bank opening line.",
        "Receivables 35,000: 'Old customer AR settlement' received 10 Jan; no 2026 invoice matches it.",
        "Inventory 80,000: warehouse notes. PPE 180,000 / 45,000: asset register.",
        "Payables 45,000: bank supplier payments 378,000 less the part paid on 2026 invoices (459,000 - 126,000); all on Event Things Europe.",
        "Payroll 15,000: payroll file. Loan 100,000: signed bank confirmation. Equity is the balancing figure.",
    ],
}

schedules = {
    "openingBalances": opening,
    "revenueAndReceivables": {
        "revenue": revenue_lines, "totalRevenue": rev,
        "excludedFromRevenue": {"New Beginnings deposit (15 Sep)": bank["depNB"], "Fresh Freedom deposit (24 Sep)": bank["depFF"],
                                "Loan advance": bank["loanAdvance"]},
        "rollForward": {"opening": open_ar, "creditRevenue": rev, "collections": -(bank["oldAR"] + collections_2026),
                        "writeOffR17": -R17, "closingNet": ar_net},
        "closingOpenItems": open_items, "closingGross": ar_gross,
    },
    "inventoryAndCogs": {
        "rollForward": {"opening": OPEN_INV, "purchases": PURCHASES, "cogs": -PHYS_COGS, "damagedWriteOff": -DAMAGED, "closing": closing_inv},
        "count": {"Finally Single materials": 79_000, "Never Call Back materials": 42_000, "Basement stock (unsaleable)": DAMAGED,
                  "systemTotal": 143_000, "goodStockCounted": COUNT_GOOD, "unexplainedCountSurplus": COUNT_GOOD - closing_inv},
        "purchasesBySupplier": {k: v[0] for k, v in suppliers.items()},
    },
    "payroll": {
        "lines": [{"department": k, "expense": v[0], "cashPaid": v[1], "unpaid": v[0] - v[1], "classification": v[2]} for k, v in payroll.items()],
        "rollForward": {"opening": OPEN_PAYROLL, "expense": pay_exp, "paid": -pay_cash, "closing": close_payroll},
        "excluded": {"Founder 'bonus' = villa + owner card (distribution, same cash)": 110_000},
    },
    "operatingExpenses": {"lines": opex, "total": sum(opex.values())},
    "ppeAndDepreciation": {
        "cost": {"opening": OPEN_PPE, "Pack-O-Matic 9000 (10 May)": bank["capexPack"], "Regret Photo Booth (10 May)": bank["capexPhoto"], "closing": ppe_cost},
        "accumulatedDepreciation": {"opening": OPEN_AD, "charge": DEPN, "closing": acc_dep},
        "netBookValue": ppe_cost - acc_dep,
        "expensedNotCapitalised": {"Repair R-771 (belt, calibration)": bank["repair"]},
    },
    "debtAndInterest": {
        "principal": {"opening": OPEN_LOAN, "advance1Mar": bank["loanAdvance"], "repaid": -bank["principal"], "closing": close_loan, "bankConfirmation": 131_000},
        "interest": {"openingPayable": 0, "expense": INT_EXP, "paid": -bank["interest"], "closingPayable": int_payable, "bankConfirmation": 2_000},
    },
    "suppliers": {
        "lines": [{"supplier": k, "invoiced": v[0], "paid": v[2], "unpaidConfirmed": v[1]} for k, v in suppliers.items()],
        "rollForward": {"openingDerived": open_ap, "purchases": PURCHASES, "paid": -sup_paid, "closing": sup_unpaid},
    },
    "equityAndDistributions": {
        "opening": opening_equity, "netProfit": net_profit,
        "distributions": {"Sunset Villa reservation": -bank["villa"], "Chairman's platinum card": -bank["ownerCard"]},
        "closing": closing_equity,
    },
    "provisions": {"Legal claim (former employee)": {"amount": LEGAL, "range": [20_000, 30_000], "basis": "Counsel best estimate, probable"}},
}

submission = {
    "schemaVersion": "1.0",
    "caseId": "DPI-HT-01",
    "student": {"id": "AP18259", "name": "Ance Petrovica"},
    "reportingDate": "2026-08-31", "currency": "EUR",
    "method": {
        "agent1": "First AI analysis: extracted evidence and proposed treatments for all 100 decisions (ai-trail/agent1.json).",
        "agent2": "Independent AI analysis from the original evidence only, without seeing Agent 1 (ai-trail/agent2.json).",
        "certification": "The student compared both analyses after completion, resolved disagreements and certified each final answer.",
        "untrustedInstructions": "Instructions embedded in evidence (e.g. 'report profit of 312,000') were treated as evidence of pressure and not followed.",
    },
    "evidence": [{"id": i, "file": f, "type": t, "summary": s, "reliability": r} for i, f, t, s, r in EVIDENCE],
    "decisions": decisions,
    "schedules": schedules,
    "statements": {"profitAndLoss": pl, "cashFlow": cf, "balanceSheet": bs},
    "reconciliations": [{"name": n, "calculation": c, "difference": d, "status": "pass"} for n, c, d in checks],
    "uncertainties": uncertainties,
    "boardRecommendation": board,
    "keyFigures": {"netProfit": net_profit, "closingCash": close_cash, "totalAssets": total_assets,
                   "totalLiabilities": total_liab, "closingEquity": closing_equity, "openingEquity": opening_equity,
                   "revenue": rev, "ownerDistributions": distributions},
}

(ROOT / "submission.json").write_text(json.dumps(submission, indent=2, ensure_ascii=False) + "\n")
print(f"submission.json written: {len(decisions)} decisions, profit {net_profit:,}, cash {close_cash:,}, "
      f"assets {total_assets:,}, liabilities {total_liab:,}, equity {closing_equity:,}; all {len(checks)} checks pass")
