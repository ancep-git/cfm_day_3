# Ball Bearing Contract Auction: budget workbook

`BB_Budget.xlsx` works out profit and loss for each contract and for the year. Every calculated cell is a live Excel formula that points to the input cells, so you can change anything in Excel without running Python again.

| File | Purpose |
|---|---|
| `BB_Budget.xlsx` | The workbook |
| `build_workbook.py` | Rebuilds the workbook from scratch (`python build_workbook.py`, needs `openpyxl`) |
| `check_workbook.py` | Recalculates copies of the workbook in LibreOffice (headless) and checks them against the expected Year 1 results and the C09 = 30 test. The delivered file is never changed. |

**Colour key:** blue text on a light-blue fill is an input. Black text is a formula. Green text is a link to another sheet. A yellow fill marks a value to confirm (C09's quantity, which was crossed out on the contract card). An orange price is outside the case range of 16,000 to 26,000.

## Sheets

- **Inputs:** rejection rate, wage coefficient, Gold price, price range, raw-material tier table, fixed expenses and market sizes.
- **Summary:** Years 1–3 side by side, with cumulative operating profit.
- **Contracts Y1 / Y2 / Y3:** one row per contract, with 30 rows per year.
- **P&L Y1 / Y2 / Y3:** a *Year total* column (column B, frozen so it stays visible), then one column for each contract row.

## Add a contract

1. On the right **Contracts Yn** sheet, find the first empty row.
2. Type the **Contract ID**, choose the **Spec** from the dropdown (Blue / Silver / Copper / Gold), and type the **Accepted qty** and **Price per BB**. You can also enter **Other direct** costs (blank counts as 0).
3. Everything else fills in by itself: production, rejects, tier price, revenue, costs, margin and break-even. The contract also gets its own column on the matching P&L sheet, and it is counted in the year total and the Summary.

Each contract is its own purchase order. Its raw-material tier comes only from its own production quantity.

## Remove a contract

Select the contract's input cells (Contract ID, Spec, Accepted qty, Price, Other direct) and press **Delete**. When the ID is blank, the row's formulas return blank. **Do not delete the whole row**, because that shrinks the 30-row range. To free up space in the middle, clear the row, or copy the input cells of the rows below up by one.

Need more than 30 contracts in a year? Insert rows *above* the Total row and copy a formula row down. The totals and the P&L year total adjust to the new range. The P&L sheet only has 30 contract columns, so copy the last contract column across for each new row as well.

## Set the Gold price

When the price is announced, go to **Inputs B7** and pick 4,500, 5,000 or 5,500 from the dropdown. The default is 5,500. It applies to every contract with Spec = Gold, and Gold does not use the tier table.

## Fill in Year 2 and Year 3

Type the contracts into **Contracts Y2** and **Contracts Y3**, the same way as Year 1. **P&L Y2 / Y3** and the **Summary** update by themselves. Market size grows from Year 1 by the growth rates on Inputs (+20%, then +10%). All years use the same tier table, rates and fixed expenses from Inputs.

Fixed expenses (200,000) are charged every year. A year with no contracts entered yet will therefore show an operating loss of 200,000 in the Summary.

## Year 1 results (checked by `check_workbook.py`)

| | C05 Silver | C08 Silver | C09 Copper | Year 1 |
|---|---|---|---|---|
| Revenue | 270,000 | 440,000 | 260,000 | 970,000 |
| Contribution margin | (32,400) | (30,400) | (8,800) | (71,600) |
| Break-even price per BB | 20,160 | 11,760 | 6,720 | |
| Operating profit | | | | (271,600) |

The file is saved without cached values, and Excel recalculates it when you open it. Some file previewers do not recalculate, so they may show blank cells.
