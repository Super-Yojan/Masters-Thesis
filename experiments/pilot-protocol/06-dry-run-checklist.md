# Dry run with Yojan (before Nov week 1)

One full trial per condition in the chosen venue, Yojan as operator, using the
protocol card exactly as written. Tick only what was seen to work.

## A. ARGOS can set and hold each level

Known from the code (ARGOS `763bad7`, Terra `52c1a0d`):

- ARGOS shows every level button at all times; nothing stops the operator from leaving a fixed condition.
- Terra's `autonomy/status` has an `assigned_level` field, but nothing sets it, so the log cannot say which condition was assigned.
- `target_search` appears in Terra's `supported_levels` only while a detector publishes fresh classes.
- L4 Explore is refused in GPS navigation mode ("Switch navigation to Local before exploring").

So "the dashboard can enforce the condition" is **not true today**. Q16 below.

For each level in the fixed set (Q3):

- [ ] L0: select it, drive 10 m, release keys; rover stops within the 500 ms lease. `autonomy/status` shows `requested_level = teleop`, `effective_level = teleop`.
- [ ] L1: same, and drive toward an obstacle; rover blocks it.
- [ ] L2: place 3 waypoints; rover drives them straight. Effective level `waypoint_direct`.
- [ ] L3: place 3 waypoints with an obstacle on the line; rover avoids or stops. Effective level `waypoint`.
- [ ] L4: start with the 10 min budget in Local mode; rover explores; the run status counts down; it ends on budget. Effective level `explore`.
- [ ] Free: switch L3 → L0 → L4 → L3 in one trial; each switch appears in both ARGOS and Terra logs with the same token.
- [ ] Stop and takeover from each level work in one click and are logged.
- [ ] Resume after a latched pause works, and the pause is logged with its cause.
- [ ] With N = 3 (if in the plan): level changes go to the intended rover only; a fleet action reaches all three.

## B. Logs, end to end

- [ ] ARGOS `argos-session-*.jsonl` found in the temp directory and copied out before quitting. (No export button in the app; Q17.)
- [ ] One Terra run log per rover (TerraPhone "Share run log", or Zorvane `<run_id>.jsonl`), not split by a mid-trial reset.
- [ ] `terra-run-summary` runs on each Terra log and the numbers match what happened (mode changes, takeovers, near misses).
- [ ] ARGOS `action_sent` tokens match Terra receipts; teleop sequence numbers line up; no intervention is counted twice.
- [ ] `experiment/status` UTC offsets let ARGOS and Terra times be placed on one timeline within 1 s.
- [ ] Neither log reports `recording: false` or dropped records.
- [ ] Time on each level can be computed from the ticks (script to write).
- [ ] Observed free area per rover is in the ticks, and the fleet total can be computed (script to write).
- [ ] `trial.json` labels filled in and saved next to the logs.
- [ ] Raw TLX filled in after the condition and saved as `tlx.csv`.
- [ ] The primary endpoint (Q15) computed from this dry run's files alone, with no memory of the session.

## C. Procedure

- [ ] Setup (placement, heading lock, GPS ≤ 10 m, recorders on) done before "go", and its duration noted.
- [ ] Trial stopped at exactly 10 min of mission time.
- [ ] Each stop rule tried once on purpose (e.g. hold not cleared) and the trial marked incomplete.
- [ ] The written instructions read aloud take under 2 minutes and answer every question the operator had.
- [ ] Whole session time measured, to size the consent text and the schedule.

## Gaps that need a decision before the pilot

- **Q16. Enforcing a fixed condition.** Options: (a) a small ARGOS "study mode" that takes a condition, disables the other level buttons (stop and L0 takeover stay enabled), and writes the condition into the session manifest, with Terra's `assigned_level` set from it; (b) enforce by instruction only and log violations from `action_sent`. (a) is a code change in ARGOS and Terra before Oct 31. Not decided.
- **Q17. Exporting ARGOS logs.** Options: (a) add an "Export session" button, or write the session log to a chosen folder instead of the temp directory; (b) copy the temp file by hand after each trial. Not decided.
