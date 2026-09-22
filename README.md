# cfm_day_3: DPI-HT-01 Financial Crime Scene

Reconstruction of Divorce Party International Ltd. at 31 August 2026: the three statements, supporting schedules, the 100 certified decisions, reconciliations, uncertainty and the board recommendation.

| Route | What it shows |
|---|---|
| `/` | Evidence, decisions, schedules, statements, reconciliations, uncertainty, board recommendation, AI review trail |
| `/review` | Compact assessor view: agent disagreements, student overrides, low-confidence decisions, unresolved uncertainty |
| `/submission.json` | Machine-readable answer (validates against `tools/submission-rules.schema.json`) |

## Key figures (EUR)

Net profit 65,000 (management claimed 312,000) · closing cash 60,000 · total assets 531,000 · liabilities 406,000 · equity 125,000.

## How it was built

1. **Agent 1** analysed the original evidence and proposed treatments (`ai-trail/agent1.json`).
2. **Agent 2** analysed the same original evidence independently, without seeing Agent 1 (`ai-trail/agent2.json`).
3. The two were compared, disagreements were resolved, and final answers were certified in `tools/build_submission.py`.
4. `python3 tools/build_submission.py` computes every schedule and statement from the source figures. It asserts all reconciliations and writes `submission.json`.

## Deploy on Vercel

Import this GitHub repository at vercel.com/new, choose the **Other** framework preset, leave the build command and output directory empty, and deploy. `vercel.json` enables clean URLs, so `/review` serves `review.html`.
