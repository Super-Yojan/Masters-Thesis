# Stress test: what is still not comparable between conditions

Read against drafts 01–06. Each item is something that would make a difference
between conditions come from the setup rather than from the level. Severity:
**blocker** (the comparison is invalid until fixed), **major** (needs a rule or a
covariate), **minor** (note it in the methods).

| # | Problem | Severity | Fix in the drafts / what remains |
|---|---|---|---|
| 1 | **Fixed is not enforced.** Every ARGOS level button stays live, and `assigned_level` is always null. A "Fixed L3" trial can contain L0 driving, and the log cannot tell what was assigned. | Blocker | Q16 (study mode) or, at minimum, label the condition by hand and treat any off-condition `action_sent` as a protocol violation. |
| 2 | **Intervention count means different things at different levels.** At L0/L1 the operator drives all the time; at L2/L3 every goal is a "redirect"; at L4 Explore the operator sets one budget and waits. Comparing intervention rates across levels compares definitions. | Blocker for endpoint C as primary | Primary endpoint must be defined at every level (Q15: coverage or interaction time). Report intervention rate only within L2–L4 and Free. |
| 3 | **The task suits some levels by construction.** Ball collection needs L0/L1 for the final approach; route scouting makes L4 pointless; find-a-target needs `target_search`. | Major | Draft task is cover-a-sector (Q5), which every fixed level can attempt. Any other task needs its own rationale per level. |
| 4 | **L4 has a budget and a stop condition the others lack.** Explore ends on its own (budget, no frontier, stale map). An L4 trial can idle while L3 never does. | Major | Fixed 10 min trial independent of the budget; restart L4 when it ends early, and log restarts as operator actions. |
| 5 | **Outdoor gates hit autonomous levels only.** GPS > 10 m or heading > ±35° holds L2/L3 missions; L0/L1 drive on regardless. L4 cannot use GPS mode at all. On Field 3, weather becomes part of the level effect. | Major (field venue) | Log every hold and its duration; report hold time as a covariate; run all conditions for one operator in one session. Simulator avoids most of it. |
| 6 | **L4 runs in a different frame outdoors.** In Local mode its map is not on Field 3 coordinates, so its coverage is not on the same map as L2/L3 waypoint runs. | Major (field venue) | Measure coverage per rover in the rover's own map, the same way at every level, or keep L4 to the simulator (Q4). |
| 7 | **N is confounded with venue** if only one physical rover works. Any N effect would equally be a sim-vs-real effect. | Major | Q6. Keep each N × level comparison inside one venue. |
| 8 | **Free is always last** in the draft order, so Free gets the most practice. | Major | Q9. Either accept and state it, or counterbalance Free and give a longer training block first. |
| 9 | **Learning across fixed levels.** Few operators, each doing every level; later levels benefit from map and field knowledge. | Major | Latin square across operators; same training per level; same start pose and sector each trial; report trial index. |
| 10 | **The builder as operator.** Yojan knows the system's failure modes; data from Yojan is not comparable with non-builder operators. | Major | Use Yojan's trials as dry-run only, or report them as a separate operator group (Q8). |
| 11 | **Setup time differs by level.** Heading lock, GPS wait, placing a 10-minute Explore. If the trial clock starts at different points, completion times differ. | Major | "Go" after setup at every level; setup logged but not scored. |
| 12 | **Mid-trial resets split logs.** A TerraPhone `reset()` closes the run log and opens a new one; a trial could have two Terra files with different run IDs. | Minor | A trial with a reset is repeated, or its files are joined by UTC and the trial flagged. |
| 13 | **L4's content varies.** `target_search` is part of L4 but appears only when a detector is fresh, so two L4 (or Free) trials may offer different controls. | Major | Q18: log Search availability per trial, or keep Search out of Fixed L4 until a detector runs in the venue. |
| 14 | **Supervised is still clickable.** It is out of the design, but ARGOS still shows the button. | Minor | Treat any `supervised` request as a protocol violation; a study mode (Q16) would hide it. |
| 15 | **Simulator idealisation.** Zorvane's perfect GPS and physics make L2 look better than it will on turf (no drift, no wheel slip). | Minor for the pilot | Label venue on every result; never pool sim and field. |
| 16 | **Link quality is uncontrolled.** No injected loss, but real Wi-Fi/router drops still happen and affect L0/L1 (lease expiry) more than L3. | Minor | Count link gaps > 1 s per trial and report them; no derived drop counter exists yet. |

## Bottom line

Items 1 and 2 have to be fixed before Nov week 1 or the pilot cannot compare
levels. Items 3–11 and 13 each need one rule on the protocol card, and most of those
rules are already drafted, pending Yojan's choices (Q3–Q9, Q12, Q15, Q18). Items 12 and 14–16
are methods notes.
