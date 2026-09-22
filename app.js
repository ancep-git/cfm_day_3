// Renders the DPI-HT-01 case from /submission.json (static data, no backend).
const eur = (n) => (n === null || n === undefined ? "–" : (n < 0 ? "(" : "") + Math.abs(n).toLocaleString("en-GB") + (n < 0 ? ")" : ""));
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const pill = (text, cls) => `<span class="pill ${cls}">${esc(text)}</span>`;
const $ = (id) => document.getElementById(id);

function kpis(k) {
  const items = [
    ["Net profit", k.netProfit, "management claimed 312,000"],
    ["Closing cash", k.closingCash, "= bank = roll-forward"],
    ["Revenue", k.revenue, "delivered only"],
    ["Total assets", k.totalAssets, ""],
    ["Total liabilities", k.totalLiabilities, ""],
    ["Closing equity", k.closingEquity, `opening ${eur(k.openingEquity)}`],
    ["Owner distributions", k.ownerDistributions, "villa + owner card"],
  ];
  return `<div class="kpis">${items.map(([l, v, s]) => `<div class="kpi"><div class="label">${l}</div><div class="value">€${eur(v)}</div><div class="sub">${s}</div></div>`).join("")}</div>`;
}

function lineTable(title, block, opts = {}) {
  const sign = opts.negate ? -1 : 1;
  const rows = Object.entries(block.lines).map(([k, v]) => `<tr><td>${esc(k)}</td><td class="num">${eur(sign * v)}</td></tr>`).join("");
  return `<tr class="sub"><td colspan="2">${esc(title)}</td></tr>${rows}<tr class="sub"><td>Total ${esc(title.toLowerCase())}</td><td class="num">${eur(sign * block.total)}</td></tr>`;
}

function renderStatements(s) {
  const pl = s.profitAndLoss, cf = s.cashFlow, bs = s.balanceSheet;
  const plHtml = `<table><tbody>
    ${lineTable("Revenue", pl.revenue)}
    ${lineTable("Cost of sales", pl.costOfSales, { negate: true })}
    <tr class="total"><td>Gross profit</td><td class="num">${eur(pl.grossProfit)}</td></tr>
    ${lineTable("Operating expenses", pl.operatingExpenses, { negate: true })}
    <tr class="total"><td>Operating profit</td><td class="num">${eur(pl.operatingProfit)}</td></tr>
    <tr><td>Interest expense</td><td class="num">${eur(-pl.interestExpense)}</td></tr>
    <tr class="total"><td>Net profit</td><td class="num">${eur(pl.netProfit)}</td></tr></tbody></table>
    <h3>Bridge from management profit</h3><table><tbody>${pl.managementBridge.map((b) => `<tr><td>${esc(b.line)}</td><td class="num">${eur(b.amount)}</td></tr>`).join("")}</tbody></table>`;
  const cfHtml = `<table><tbody>
    ${lineTable("Operating activities", cf.operating)}
    ${lineTable("Investing activities", cf.investing)}
    ${lineTable("Financing activities", cf.financing)}
    <tr class="total"><td>Net change in cash</td><td class="num">${eur(cf.netChange)}</td></tr>
    <tr><td>Opening cash</td><td class="num">${eur(cf.openingCash)}</td></tr>
    <tr class="total"><td>Closing cash</td><td class="num">${eur(cf.closingCash)}</td></tr></tbody></table>
    <h3>Indirect method (reconciles to operating cash flow)</h3><table><tbody>${lineTable("Operating cash flow", cf.indirectReconciliation)}</tbody></table>
    <p class="muted">${esc(cf.note)}</p>`;
  const bsHtml = `<table><tbody>
    ${lineTable("Assets", bs.assets)}
    ${lineTable("Liabilities", bs.liabilities)}
    ${lineTable("Equity", bs.equity)}
    <tr class="total"><td>Liabilities + equity</td><td class="num">${eur(bs.liabilitiesAndEquity)}</td></tr></tbody></table>
    <p class="muted">${esc(bs.liabilities.note)}</p>`;
  return { plHtml, cfHtml, bsHtml };
}

function renderRecon(recs) {
  return `<table><thead><tr><th>Check</th><th>Calculation</th><th class="num">Difference</th><th>Status</th></tr></thead><tbody>${recs
    .map((r) => `<tr><td>${esc(r.name)}</td><td>${esc(r.calculation)}</td><td class="num">${eur(r.difference)}</td><td>${pill(r.status, r.status)}</td></tr>`)
    .join("")}</tbody></table>`;
}

function renderObj(obj) {
  // Generic renderer for schedule objects: nested key/value tables.
  if (Array.isArray(obj)) {
    if (obj.length && typeof obj[0] === "object") {
      const cols = Object.keys(obj[0]);
      return `<div class="scroll"><table><thead><tr>${cols.map((c) => `<th${typeof obj[0][c] === "number" ? ' class="num"' : ""}>${esc(c)}</th>`).join("")}</tr></thead><tbody>${obj
        .map((r) => `<tr>${cols.map((c) => (typeof r[c] === "number" ? `<td class="num">${eur(r[c])}</td>` : `<td>${esc(r[c])}</td>`)).join("")}</tr>`)
        .join("")}</tbody></table></div>`;
    }
    return `<ul class="tight">${obj.map((x) => `<li>${esc(Array.isArray(x) ? x.map(eur).join(" – ") : x)}</li>`).join("")}</ul>`;
  }
  return `<table><tbody>${Object.entries(obj)
    .map(([k, v]) =>
      v !== null && typeof v === "object"
        ? `<tr><td colspan="2"><strong>${esc(k)}</strong>${renderObj(v)}</td></tr>`
        : `<tr><td>${esc(k)}</td>${typeof v === "number" ? `<td class="num">${eur(v)}</td>` : `<td>${esc(v)}</td>`}</tr>`
    )
    .join("")}</tbody></table>`;
}

const LABELS = {
  openingBalances: "Opening balances (1 Jan 2026)", revenueAndReceivables: "Revenue and receivables", inventoryAndCogs: "Inventory and COGS",
  payroll: "Payroll", operatingExpenses: "Operating expenses", ppeAndDepreciation: "PPE and depreciation", debtAndInterest: "Debt and interest",
  suppliers: "Supplier payables", equityAndDistributions: "Equity and distributions", provisions: "Provisions",
};

function effectStr(e) {
  if (!e) return "–";
  return ["profit", "cash", "assets", "liabilities", "equity"].map((k) => `${k} ${e[k] === null ? "n/a" : eur(e[k])}`).join(" · ");
}

function decisionFlags(d) {
  const f = [];
  if (d.reviewTier === "material_judgment") f.push(pill("material", "mat"));
  if (d.agentsAgree === false) f.push(pill("agents disagree", "flag"));
  if (d.changedFromAI) f.push(pill("student override", "over"));
  f.push(pill(d.confidence, d.confidence));
  return f.join(" ");
}

function decisionCard(d) {
  const mat = d.reviewTier === "material_judgment";
  const body = mat
    ? `<div class="trail">
        <div><h4>First AI proposal (Agent 1)</h4>${esc(d.aiProposal.answer)}<div class="effect muted">${effectStr(d.aiProposal.statementEffect)}</div></div>
        <div><h4>Independent challenge (Agent 2)</h4>${esc(d.independentChallenge)}</div>
        <div><h4>Certified final answer</h4>${esc(d.answer)}<p><strong>Reasoning:</strong> ${esc(d.studentReasoning)}</p>
        <div class="effect">${effectStr(d.statementEffect)}</div></div></div>`
    : `<p>${esc(d.answer)}</p>`;
  return `<details data-id="${d.id}"><summary><span class="id">${d.id}</span><strong>${esc(d.question)}</strong> ${decisionFlags(d)}</summary>
    ${body}<div class="muted" style="font-size:13px;margin-top:6px">Evidence: ${d.evidence.map(esc).join("; ")}</div></details>`;
}

function renderUncertainty(us) {
  return `<div class="scroll"><table><thead><tr><th>Item</th><th>Profit effect range</th><th>Confidence</th><th>Decisions</th><th>Note</th></tr></thead><tbody>${us
    .map((u) => `<tr><td>${esc(u.item)}</td><td>${esc(u.profitEffectRange)}</td><td>${pill(u.confidence, u.confidence)}</td><td class="id">${u.decisions.join(", ")}</td><td>${esc(u.note)}</td></tr>`)
    .join("")}</tbody></table></div>`;
}

function renderBoard(b) {
  return `<div class="callout"><strong>${esc(b.headline)}</strong></div>
    <p><strong>Profit range:</strong> €${eur(b.profitRange.low)} – €${eur(b.profitRange.high)} (base €${eur(b.profitRange.base)}). <span class="muted">${esc(b.profitRange.note)}</span></p>
    <h3>Working-capital and solvency warning</h3><p>${esc(b.workingCapitalWarning)}</p>
    <h3>Five immediate control actions</h3><ol>${b.controlActions.map((a) => `<li>${esc(a)}</li>`).join("")}</ol>
    <h3>Should the core business continue?</h3><div class="callout good">${esc(b.decisionOnCoreBusiness)}</div>
    <p><strong>Earn-out:</strong> ${esc(b.earnOut)}</p>`;
}

async function load() {
  const res = await fetch("/submission.json");
  return res.json();
}

async function mainPage() {
  const s = await load();
  $("student").textContent = `${s.student.name} · ${s.student.id} · ${s.caseId} · reporting date ${s.reportingDate}`;
  $("kpis").innerHTML = kpis(s.keyFigures);
  $("board").innerHTML = renderBoard(s.boardRecommendation);
  const st = renderStatements(s.statements);
  $("pl").innerHTML = st.plHtml; $("cf").innerHTML = st.cfHtml; $("bs").innerHTML = st.bsHtml;
  $("recon").innerHTML = renderRecon(s.reconciliations);
  $("schedules").innerHTML = Object.entries(s.schedules)
    .map(([k, v]) => `<details><summary><strong>${esc(LABELS[k] || k)}</strong></summary><div class="scroll">${renderObj(v)}</div></details>`).join("");
  $("uncertainty").innerHTML = renderUncertainty(s.uncertainties);
  $("evidence").innerHTML = `<div class="scroll"><table><thead><tr><th>ID</th><th>File</th><th>Type</th><th>What it shows</th><th>Reliability</th></tr></thead><tbody>${s.evidence
    .map((e) => `<tr><td class="id">${e.id}</td><td>${esc(e.file)}</td><td>${esc(e.type)}</td><td>${esc(e.summary)}</td><td>${pill(e.reliability, e.reliability)}</td></tr>`).join("")}</tbody></table></div>
    <p class="muted">${esc(s.method.agent1)} ${esc(s.method.agent2)} ${esc(s.method.certification)} ${esc(s.method.untrustedInstructions)}</p>`;
  $("trail").innerHTML = s.decisions.filter((d) => d.reviewTier === "material_judgment").map(decisionCard).join("");

  const draw = () => {
    const q = $("q").value.toLowerCase(), tier = $("tier").value, cat = $("cat").value;
    const list = s.decisions.filter((d) =>
      (!tier || d.reviewTier === tier) && (!cat || d.category === cat) &&
      (!q || (d.id + d.question + d.answer + d.evidence.join(" ")).toLowerCase().includes(q)));
    $("count").textContent = `${list.length} of ${s.decisions.length} decisions`;
    $("decisions").innerHTML = list.map(decisionCard).join("");
  };
  const cats = [...new Set(s.decisions.map((d) => d.category))];
  $("cat").innerHTML = `<option value="">All categories</option>${cats.map((c) => `<option>${c}</option>`).join("")}`;
  ["q", "tier", "cat"].forEach((id) => $(id).addEventListener("input", draw));
  draw();
}

async function reviewPage() {
  const s = await load();
  const D = s.decisions;
  const mat = D.filter((d) => d.reviewTier === "material_judgment");
  const disagree = D.filter((d) => d.agentsAgree === false);
  const overrides = D.filter((d) => d.changedFromAI);
  const low = D.filter((d) => d.confidence === "low");
  const unresolved = s.uncertainties.filter((u) => u.confidence === "low" || u.low === null);
  const allPass = s.reconciliations.every((r) => r.status === "pass");
  $("student").textContent = `${s.student.name} · ${s.student.id} · ${s.caseId}`;
  $("kpis").innerHTML = kpis(s.keyFigures) +
    `<div class="kpis" style="margin-top:10px">
      <div class="kpi"><div class="label">Decisions</div><div class="value">${D.length}</div><div class="sub">${D.length - mat.length} operational · ${mat.length} material</div></div>
      <div class="kpi"><div class="label">Reconciliations</div><div class="value">${s.reconciliations.filter((r) => r.status === "pass").length}/${s.reconciliations.length}</div><div class="sub">${allPass ? "all pass" : "FAILURES"}</div></div>
      <div class="kpi"><div class="label">Agent disagreements</div><div class="value">${disagree.length}</div></div>
      <div class="kpi"><div class="label">Student overrides</div><div class="value">${overrides.length}</div></div>
      <div class="kpi"><div class="label">Low confidence</div><div class="value">${low.length}</div></div>
      <div class="kpi"><div class="label">Unresolved uncertainty</div><div class="value">${unresolved.length}</div></div></div>`;
  const brief = (list) => `<table><tbody>${list.map((d) => `<tr><td class="id"><a href="#${d.id}">${d.id}</a></td><td>${esc(d.question)}</td><td>${decisionFlags(d)}</td></tr>`).join("")}</tbody></table>`;
  $("disagree").innerHTML = brief(disagree) + `<p class="muted">Agent 1 and Agent 2 disagreed on the 9,000 inventory count surplus and on accruing the 2,000 disposal cost; D089, D091 and D100 differ only in the resulting profit figure (63,000 vs 65,000).</p>`;
  $("overrides").innerHTML = overrides.map((d) =>
    `<div class="trail" style="margin-bottom:10px"><div><h4>${d.id} · Agent 1 proposed</h4>${esc(d.aiProposal.answer)}</div><div><h4>Certified</h4>${esc(d.answer)}</div><div><h4>Why</h4>${esc(d.studentReasoning)}</div></div>`).join("");
  $("low").innerHTML = brief(low);
  $("unresolved").innerHTML = renderUncertainty(unresolved);
  $("recon").innerHTML = renderRecon(s.reconciliations);
  $("board").innerHTML = renderBoard(s.boardRecommendation);
  $("trail").innerHTML = `<div class="scroll"><table><thead><tr><th>ID</th><th>Decision</th><th>Certified answer</th><th>Effect (P · cash · A · L · E)</th><th>Flags</th></tr></thead><tbody>${mat
    .map((d) => `<tr id="${d.id}"><td class="id">${d.id}</td><td>${esc(d.question)}</td><td>${esc(d.answer)}</td><td class="effect">${["profit", "cash", "assets", "liabilities", "equity"].map((k) => eur(d.statementEffect[k])).join(" · ")}</td><td>${decisionFlags(d)}</td></tr>`).join("")}</tbody></table></div>`;
  $("all").innerHTML = `<div class="scroll"><table><thead><tr><th>ID</th><th>Question</th><th>Answer</th><th>Flags</th></tr></thead><tbody>${D.filter((d) => d.reviewTier === "operational")
    .map((d) => `<tr id="${d.id}"><td class="id">${d.id}</td><td>${esc(d.question)}</td><td>${esc(d.answer)}</td><td>${decisionFlags(d)}</td></tr>`).join("")}</tbody></table></div>`;
}

(document.body.dataset.page === "review" ? reviewPage : mainPage)().catch((e) => {
  document.querySelector("main").insertAdjacentHTML("afterbegin", `<div class="callout">Could not load submission.json: ${esc(e.message)}</div>`);
});
