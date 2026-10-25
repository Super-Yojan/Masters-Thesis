# Level contract (pilot, draft for freeze by 2026-10-31)

One page. Each row is what an operator must be able to tell apart. If two rows
feel the same from the operator station, merge them or drop one: factor A is
only as good as this table.

Sources: thesis `introduction.tex` (Table `tab:intro-levels`), `ch2_competition.tex`
§`sec:env-explore`, `ch5_autonomy.tex`; ARGOS `crates/argos-core/src/autonomy.rs`
(`OPERATOR_LEVELS`), `crates/argos-core/src/exploration.rs`; Terra
`crates/terra-autonomy/src/arbiter/status.rs` (`supported_levels`). Revisions read:
ARGOS `763bad7`, Terra `52c1a0d`.

| Level | ARGOS button | Wire name | Robot does | Operator does | Local planner (avoidance) | Outdoor (GPS) on Field 3 |
|---|---|---|---|---|---|---|
| L0 | L0 Manual | `teleop` | Nothing on its own. Stops when the 500 ms teleop lease expires. | Holds keys to drive every metre. | Off | Allowed (no GPS needed). |
| L1 | L1 Assisted | `assisted_teleop` | Blocks or slows motion toward obstacles. Stops on lease expiry. | Holds keys to drive. | On (as a filter on operator commands) | Allowed (no GPS needed). |
| L2 | L2 Direct | `waypoint_direct` | Drives straight to each goal. Does not avoid. | Places each waypoint, watches, stops it before a collision. | Off | Allowed when the fix is within 10 m and heading uncertainty is within ±35°; otherwise ARGOS holds. |
| L3 | L3 Waypoint | `waypoint` | Drives to each goal and stops for or steers around obstacles. Keeps an accepted goal through a router outage. | Places each waypoint. | On | Same GPS and heading gates as L2. |
| L4 | L4 Explore | `explore` | Picks frontiers itself for a 3, 5 or 10 min budget. Ends on budget, no frontier, stale map (>0.5 s), hold, stop or takeover. | Starts it with a budget, watches, takes over. | On (horizon 1 s) | **Not in GPS mode today.** ARGOS refuses explore unless navigation is set to Local (`explore_refusal`). On Field 3 it runs in the rover's local frame only. |
| (mode) | Supervised | `supervised` | Same frontiers as L4, but waits for approval of each one. | Approves or rejects every frontier. | On | Same as L4 (assumed; not checked). |
| (L4?) | Search | `target_search` | Searches an area for a detector class and confirms targets. | Sets area, class, budget; confirms. | On | Offered by Terra only while a detector is publishing fresh classes. Not validated on hardware (thesis intro, Current status). |
| L5 | none | none | Not implemented. | | | **Dropped from the study.** |

Rules that hold at every level, and so are not part of the factor:

- Stop and L0 takeover are one click away in ARGOS at every level.
- Any loss of GPS, heading, tracking, map, arming or authority latches a pause. Only the operator's Resume clears it.
- Terra keeps motion authority on the phone; ARGOS sends intent, not velocity (except held teleop at L0 and L1).

## Decisions only Yojan can make

- **Q1. What is L4?** The thesis says L4 = `explore` + `target_search`. ARGOS labels only `explore` as "L4 Explore" and keeps `target_search` as a separate "Search" button. Options: (a) L4 = `explore` only for the pilot, `target_search` out of the study until detection is validated on hardware; (b) L4 = `explore`, and `target_search` becomes its own condition later; (c) keep the thesis wording and report both as L4. *Draft recommendation: (a), and update Table `tab:intro-levels` to match.* Not decided.
- **Q2. Is Supervised a level or a mode?** It reuses L4's frontiers and adds per-goal approval, which is closer to "L4 with a human in the loop" than to a rung of its own. Options: (a) a mode on L4, not a pilot condition; (b) a separate pilot condition; (c) a mode that can apply to L3 and L4 (approval of each waypoint/frontier). *Draft recommendation: (a) for the pilot.* Not decided.
- **Q3. Which levels are fixed conditions in the pilot?** Every extra level multiplies trials. Candidate: L0, L2, L3, plus L4 only if it passes the dry run in the chosen venue. L0 vs L2 vs L3 isolates "operator drives" vs "robot drives, no avoidance" vs "robot drives with avoidance". L1 could be dropped from the fixed set because its difference from L0 shows only near obstacles. Not decided.
- **Q4. Is L4 allowed outdoors?** Today it is not, in GPS mode. If the pilot venue is Field 3, either L4 runs in the local frame (and the map is not on Field 3 coordinates), or L4 is a simulator-only condition. Not decided.
