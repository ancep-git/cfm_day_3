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

// The two root disagreements between the agents. D091 and D100 differ only because of these.
const DISPUTES = [
  {
    title: "Closing inventory: book roll-forward or physical count?",
    ids: ["D075"],
    question: "The roll-forward (80,000 + 459,000 - 405,000 - 22,000) gives 112,000. The physical count of good stock is 121,000. Which figure goes on the balance sheet, and where does the 9,000 go?",
    options: [
      { key: "book", label: "Book roll-forward 112,000; flag the 9,000 (Agent 2)", certified: true,
        effect: { profit: 0, assets: 0, liabilities: 0, equity: 0 },
        why: "Every input is evidenced (supplier-confirmed purchases, consumption tied to delivered sales). The count is valued at an un-updated system cost. More prudent." },
      { key: "countOpening", label: "Count 121,000; 9,000 to opening equity (Agent 1)",
        effect: { profit: 0, assets: 9000, liabilities: 0, equity: 9000 },
        why: "The count agrees with the system. The gap is treated as a pre-2026 difference. But this restates an opening balance without evidence." },
      { key: "countProfit", label: "Count 121,000; 9,000 through cost of sales (alternative Agent 1 named)",
        effect: { profit: 9000, assets: 9000, liabilities: 0, equity: 9000 },
        why: "Treats the surplus as over-stated consumption in 2026. There is no evidence that COGS of 405,000 is wrong." },
    ],
  },
  {
    title: "Damaged stock: provide for the 2,000 disposal quote?",
    ids: ["D058", "D072"],
    question: "Both agents write the basement stock down to nil (22,000). Should a further 2,000 be accrued for the disposal quote at 31 Aug?",
    options: [
      { key: "noAccrual", label: "No provision; disclose (Agent 2)", certified: true,
        effect: { profit: 0, assets: 0, liabilities: 0, equity: 0 },
        why: "No legal or constructive obligation to dispose at 31 Aug. Disposal was decided after the takeover, so it is a future operating cost. Inventory cannot go below zero." },
      { key: "accrue", label: "Accrue 2,000 (Agent 1)",
        effect: { profit: -2000, assets: 0, liabilities: 2000, equity: -2000 },
        why: "The condition (water damage) existed at 31 Aug and the quote is independent. Immaterial either way." },
    ],
  },
];
const KNOCK_ON = ["D091", "D100"];
const KEY_EFFECT = { netProfit: "profit", totalAssets: "assets", totalLiabilities: "liabilities", closingEquity: "equity" };

async function decisionsPage() {
  const [s, a1, a2] = await Promise.all(["/submission.json", "/ai-trail/agent1.json", "/ai-trail/agent2.json"].map((u) => fetch(u).then((r) => r.json())));
  const A = Object.fromEntries(a1.decisions.map((d) => [d.id, d]));
  const B = Object.fromEntries(a2.decisions.map((d) => [d.id, d]));
  const mat = s.decisions.filter((d) => d.reviewTier === "material_judgment");
  const disputed = DISPUTES.flatMap((x) => x.ids);
  const status = (d) => {
    if (disputed.includes(d.id)) return ["disputed", "flag"];
    if (KNOCK_ON.includes(d.id)) return ["knock-on only", "over"];
    if (A[d.id].confidence !== B[d.id].confidence) return ["same treatment, confidence differs", "medium"];
    return ["agree", "high"];
  };
  const counts = mat.reduce((c, d) => ((c[status(d)[0]] = (c[status(d)[0]] || 0) + 1), c), {});
  const k = s.keyFigures;
  $("kpis").innerHTML = `<div class="kpis">
    <div class="kpi"><div class="label">Material judgments</div><div class="value">${mat.length}</div><div class="sub">compared one by one</div></div>
    <div class="kpi"><div class="label">Full agreement</div><div class="value">${counts["agree"] || 0}</div><div class="sub">same treatment and confidence</div></div>
    <div class="kpi"><div class="label">Confidence only</div><div class="value">${counts["same treatment, confidence differs"] || 0}</div><div class="sub">same numbers</div></div>
    <div class="kpi"><div class="label">Disputed</div><div class="value">${counts["disputed"] || 0}</div><div class="sub">${DISPUTES.length} root issues</div></div>
    <div class="kpi"><div class="label">Knock-on only</div><div class="value">${counts["knock-on only"] || 0}</div><div class="sub">profit 63,000 vs 65,000</div></div>
    <div class="kpi"><div class="label">Certified net profit</div><div class="value">€${eur(k.netProfit)}</div><div class="sub">equity ${eur(k.closingEquity)}</div></div></div>`;

  const eff = (e) => ["profit", "assets", "liabilities", "equity"].map((f) => `${f} ${e[f] > 0 ? "+" : ""}${eur(e[f])}`).join(" · ");
  $("choices").innerHTML = DISPUTES.map((x, i) => `<h3>${i + 1}. ${esc(x.title)} <span class="id">${x.ids.join(", ")}</span></h3>
    <p>${esc(x.question)}</p>
    <div class="trail">${x.options.map((o) => `<div><h4>${esc(o.label)} ${o.certified ? pill("certified", "pass") : ""}</h4>${esc(o.why)}
      <div class="effect muted">vs certified: ${eff(o.effect)}</div></div>`).join("")}</div>`).join("") +
    `<p class="muted">Every other material judgment has the same treatment and the same numbers in both analyses. D091 (approve corrected accounts) and D100 (earn-out) agree on the decision (yes and no); they quote 63,000 or 65,000 depending on the two choices above.</p>`;

  const combos = DISPUTES[0].options.flatMap((inv) => DISPUTES[1].options.map((dis) => [inv, dis]));
  $("matrix").innerHTML = `<table><thead><tr><th>Inventory</th><th>Disposal</th><th class="num">Net profit</th><th class="num">Total assets</th><th class="num">Liabilities</th><th class="num">Equity</th><th></th></tr></thead><tbody>${combos
    .map(([inv, dis]) => {
      const add = (f) => k[f] + inv.effect[KEY_EFFECT[f]] + dis.effect[KEY_EFFECT[f]];
      const tag = inv.certified && dis.certified ? pill("certified", "pass") : inv.key === "countOpening" && dis.key === "accrue" ? pill("Agent 1", "mat") : "";
      return `<tr><td>${esc(inv.label.split(" (")[0])}</td><td>${esc(dis.label.split(" (")[0])}</td><td class="num">${eur(add("netProfit"))}</td><td class="num">${eur(add("totalAssets"))}</td><td class="num">${eur(add("totalLiabilities"))}</td><td class="num">${eur(add("closingEquity"))}</td><td>${tag}</td></tr>`;
    }).join("")}</tbody></table><p class="muted">Closing cash is 60,000 in every case. Neither choice moves cash.</p>`;

  $("table").innerHTML = `<table><thead><tr><th>ID</th><th>Decision</th><th>Agent 1</th><th>Agent 2 (independent)</th><th>Status</th><th>Certified</th></tr></thead><tbody>${mat
    .map((d) => { const [t, c] = status(d); return `<tr><td class="id">${d.id}</td><td>${esc(d.question)}</td>
      <td>${esc(A[d.id].answer)} ${pill(A[d.id].confidence, A[d.id].confidence)}</td>
      <td>${esc(B[d.id].answer)} ${pill(B[d.id].confidence, B[d.id].confidence)}</td>
      <td>${pill(t, c)}</td><td>${esc(d.answer)}</td></tr>`; }).join("")}</tbody></table>`;
}

const PAGES = { review: reviewPage, decisions: decisionsPage };
(PAGES[document.body.dataset.page] || mainPage)().catch((e) => {
  document.querySelector("main").insertAdjacentHTML("afterbegin", `<div class="callout">Could not load submission.json: ${esc(e.message)}</div>`);
});
