# Pilot study protocol (draft, freeze by 2026-10-31)

Pre-study documents for the operator pilot planned to start in the first week of
November 2026. They are drafts written from the thesis (`thesis/chapters/introduction.tex`
level table, `ch2_competition.tex` §`sec:next-study` and §`sec:env-logging`) and from
the code in ARGOS `763bad7`, Terra `52c1a0d` and Zorvane. **No design decision
is made here**: every choice is listed below as an open question with a draft
default, so the documents can be dry-run before they are frozen.

| File | Contents |
|---|---|
| [01-level-contract.md](01-level-contract.md) | L0–L4 on one page: robot, operator, planner, outdoor rules |
| [02-protocol-card.md](02-protocol-card.md) | Task, N, conditions, trial length, operators, order, stop rules |
| [03-logging-plan.md](03-logging-plan.md) | Primary endpoint candidates; what ARGOS, Terra and Zorvane log today; gaps |
| [04-ethics-and-consent.md](04-ethics-and-consent.md) | Permission path checklist and draft consent text |
| [05-venue.md](05-venue.md) | Zorvane vs Field 3 practice vs the match |
| [06-dry-run-checklist.md](06-dry-run-checklist.md) | One full trial per condition with Yojan; can ARGOS enforce each level |
| [07-comparability-stress-test.md](07-comparability-stress-test.md) | What is still not comparable between conditions |

## Open questions (Yojan decides)

| # | Question | Draft default |
|---|---|---|
| Q1 | Is L4 `explore` only, or `explore` + `target_search`? | **Decided:** `explore` + `target_search` |
| Q2 | Is Supervised a level or a mode? | **Decided:** neither; excluded from the study |
| Q3 | Which levels are fixed conditions? | L0, L2, L3 (+ L4 if it passes the dry run) |
| Q4 | Is L4 allowed outdoors (it is refused in GPS mode today)? | L4 in Local mode only, or sim only |
| Q5 | Pilot task | Cover a sector (one penalty box) |
| Q6 | Fleet sizes, and how many rovers are field-ready | N ∈ {1, 3} |
| Q7 | Trial length | 10 min mission time |
| Q8 | Who operates | Yojan for dry runs; 3–5 non-builders for the pilot |
| Q9 | Order and counterbalancing | Latin square for fixed levels; Free last |
| Q10 | Workload instrument | Raw NASA-TLX after each condition |
| Q11 | Ethics path for the pilot | **Decided:** no IRB approval needed for the pilot; main study still needs a determination |
| Q12 | Primary venue | Zorvane for Nov; Field 3 as a separate labelled block |
| Q13 | Disturbances in the pilot | None |
| Q14 | Stop-rule thresholds | 60 s uncleared hold; field boundary |
| Q15 | Primary endpoint | Fleet coverage at fixed T and N |
| Q16 | Enforce Fixed in ARGOS (study mode) or by instruction | **Decided:** enforced by an ARGOS study mode (in progress) |
| Q17 | ARGOS session export | **Decided:** export button in ARGOS (in progress) |
| Q19 | Run the pilot without recommendations (Ch6 / LLM) if they are not ready? | **Decided:** yes; recommendations off in all pilot conditions |
| Q18 | Search inside a Fixed L4 trial (detector-gated, not validated on hardware) | Allowed, availability logged per trial |

## Before Nov week 1

1. Decide the open questions above (Q15 first: without it the conditions cannot be compared).
2. Prepare consent, operator IDs and log storage (04). The pilot needs no IRB approval (Yojan, 2026-10-27).
3. Run the dry run (06) in the chosen venue and fix what breaks.
4. Freeze: copy the decided values into 01 and 02, remove the "draft" headers, tag the repo, and record the ARGOS, Terra, Zorvane and TerraPhone revisions used.
5. Then update `introduction.tex` (Table `tab:intro-levels`, the study TODO) and `ch2_competition.tex` §`sec:next-study` to match.
