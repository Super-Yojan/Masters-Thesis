# Protocol card (pilot, draft for freeze by 2026-10-31)

One page. Every cell marked **Q** is an open choice for Yojan; the value next to
it is a draft default so the card can be dry-run, not a decision.

| Item | Draft | Open question |
|---|---|---|
| Purpose of the pilot | Check that the conditions are distinguishable, the logs join end to end, and the endpoint can be computed. Not powered for hypothesis tests. | |
| Venue | One venue for the whole pilot, labelled on every trial. See `05-venue.md`. | **Q12** |
| Task | *Cover a sector*: maximise the observed free area of one penalty box within the trial time. Every fixed level can attempt it (L0/L1 by driving, L2/L3 by waypoints, L4 by exploring), and Terra already logs observed free area. Ball collection and scoring are out of the pilot. | **Q5** task choice |
| Fleet size N | N ∈ {1, 3}. Same N for every condition within a block. | **Q6** values; how many physical rovers work |
| Factor A (conditions) | Fixed L0, Fixed L2, Fixed L3, (Fixed L4), Free. In Free the operator may use any level L0–L4. Supervised is never used. | **Q3**, **Q18** |
| Trial length | 10 min of mission time per trial, from the operator's "go" to a hard stop, regardless of L4 budget. L4 is started with the 10 min budget and restarted if it ends early. | **Q7** |
| Setup outside the trial | Rover placed at the same start pose, heading locked (straight drive outdoors), GPS fix ≤ 10 m, logs recording, all before "go". Setup time is logged but not scored. | |
| Operators × trials | Draft: Yojan as dry-run operator only; 3–5 operators who did not build the rover, each doing every condition once per N. | **Q8** who; **Q11** ethics |
| Order | Fixed levels in a Latin-square order across operators; Free always last, so the operator has used each level before choosing freely. | **Q9** counterbalancing |
| Training | One 5 min practice per level in Zorvane before the first trial, same script for everyone. | |
| Instructions | Written, read aloud verbatim. Fixed: "Use only the level shown. Stop or take over only for safety." Free: "Use any level, as you see fit." | |
| Workload | Raw NASA-TLX (6 scales, unweighted) after each condition. | **Q10** instrument |
| Disturbances | None in the pilot: no injected link loss, no extra debris, no tagging. Add only after the pilot, never mid-stream. | **Q13** |
| Stop rules (trial) | End the trial early on: a contact with a person; a rover leaving the field boundary; a latched hold not cleared within 60 s; a recording failure (ARGOS or Terra `recording: false`). The trial is marked incomplete, not re-scored. | **Q14** thresholds |
| Stop rules (session) | Stop the session if an operator asks, if the same failure ends two trials in a row, or on weather that degrades GPS below the gate. | |
| Repeat rule | An incomplete trial is repeated once at the end of the session, in the same condition. The repeat is labelled. | |
| Per-trial labels | Venue, operator ID (pseudonymous), condition, N, trial index, software revisions (ARGOS, Terra, Zorvane, TerraPhone build), weather (field only), start UTC. | |

## Open questions referenced above

- **Q5. Task.** Cover-a-sector is the only task in the thesis list that every fixed level can do. Find-a-target needs `target_search` (not validated). Scout-a-route favours L2/L3 and makes L4 meaningless. Not decided.
- **Q6. Fleet sizes.** How many rovers are field-ready by Nov 2? If only one, N > 1 exists only in Zorvane and N is confounded with venue. Not decided.
- **Q7. Trial length.** 10 min matches the longest L4 budget. Shorter trials give more trials per session but make L4 restarts more frequent. Not decided.
- **Q8. Operators.** Yojan only, team members, or classmates who did not build it. The thesis says the study is designed for operators who did not build the rover (`ch2_competition.tex`). Not decided.
- **Q9. Counterbalancing.** Free-last versus fully counterbalanced. Free-last confounds Free with practice; fully counterbalanced means some operators choose freely before they have tried each level. Not decided.
- **Q10. Workload instrument.** Raw TLX is short and standard; full weighted TLX adds pairwise comparisons. Not decided.
- **Q13. Disturbances in the pilot.** Draft keeps them out. Not decided.
- **Q14. Stop-rule thresholds.** The 60 s hold timeout and the field boundary are placeholders. Not decided.
