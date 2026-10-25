# Logging plan (pilot, draft for freeze by 2026-10-31)

## Primary endpoint (Q15, not decided)

The endpoint has to be defined, with the same meaning, at every level in the
pilot. That rules out a plain intervention count: at L0 and L1 the operator
drives all the time, so "intervention" has no meaning there.

| Candidate | Defined at every level? | Already computable? | Notes |
|---|---|---|---|
| **A. Fleet coverage at fixed T and N**: observed free area of the sector after 10 min, summed over rovers | Yes | Partly: Terra logs observed free area per tick; summing across rovers is not built | Measures whether the mission gets done. Answers "minimum level that is effective" most directly. |
| **B. Operator interaction time per rover-minute** | Yes, if goal placement and approvals get a duration | Partly: `operator_control_seconds` covers teleop only; goal clicks have no duration | Closest to fan-out / neglect-time models. Needs a definition of interaction time for clicks. |
| C. Interventions per minute (takeovers + approvals + rejections + redirects) | No: zero or undefined at L0/L1 | Yes: `terra-run-summary` `interventions_per_minute` | Good secondary for L2–L4 and Free only. |
| D. Time on task under fixed N | Only if the task has an end state | Yes for mission completion | Cover-a-sector has no natural end; would need a coverage threshold. |

*Draft recommendation: A primary, B and C secondary, TLX as the workload measure.* Yojan decides.

## What already exists

**Terra (phone)**: TerraPhone writes `Documents/Terra-run-<uuid>.jsonl` from `prepare()` and shares it with the "Share run log" button. A `reset()` closes it, and the next `prepare()` opens a new file. Records include `control_tick` (requested/effective level, goal, proposal, exploration, search, clearance, events) and `runtime.event`. Note: the `run_id` inside the file is a different UUID from the one in the file name.

**Terra summary**: `terra-run-summary <run.jsonl>` (crate `terra-experiment`) prints `duration`, `mode_changes` (operator_selection), `takeovers`, `approvals`, `rejections`, `redirects`, `interventions_per_minute`, `operator_control_seconds`, `near_misses` (clearance < 0.3 m), `contacts`, `mission_complete`, search counts. `time_to_first_discovery` refers to the removed survivor mission and is unused on NEXT.

**ARGOS**: each connect writes `argos-session-<uuid>.jsonl` in the OS temp directory. Records: `manifest`, `action_sent` (level requests via `operator_command`, safety stop and reset), `teleop_sent` (with sequence), `goal_sent`, `goal_cancel_sent`, `fleet_action`, `state_observed` for `autonomy/status`, `goal/proposal`, `mission/status`, `experiment/status`. Times are session-relative monotonic plus UTC. `Client::export_session` exists in `argos-zenoh` and the FFI, but **the desktop app has no export button**: the file must be copied out of the temp directory by hand, and macOS can clear it on reboot.

**Zorvane**: writes `<run_id>.jsonl` per run (`simulator/src/bridge_recording.rs`) and publishes `experiment/status`. Fleet size via the start menu or `P/fleet/size` (0–32).

**Clock join**: `experiment/status` pairs each rover's run clock with UTC; ARGOS records it as `state_observed`. Action tokens and teleop sequence numbers join ARGOS sends to Terra receipts.

## Measures, source, and gap

| Measure | Source | Status |
|---|---|---|
| Condition, N, operator ID, venue, trial index | none | **Gap.** No field anywhere. Draft: a per-trial `trial.json` sidecar written by hand, plus a trial start/stop note. A logged ARGOS "study mode" would be better (see dry run). |
| Assigned level vs requested vs effective | Terra `autonomy/status` has `assigned_level`, `requested_level`, `effective_level` | **Gap.** `assigned_level` is never set (always null). |
| Time on each level | Terra `control_tick.status` | **Gap.** Not summarised; a short script over ticks. |
| Mode switches | Terra `mode_changes`; ARGOS `action_sent` | Exists. |
| Interventions (takeover, approve, reject, redirect) | Terra summary | Exists (Terra side). |
| Teleop exposure | Terra `operator_control_seconds` | Exists. |
| Goal placements | ARGOS `goal_sent` | Exists; no duration. |
| Holds / pauses and their cause | Terra `autonomy/status` (paused), `runtime.event` | Logged, not summarised. |
| Link drops | gaps in `state_observed` / `experiment/status` at ARGOS; Terra connectivity status | **Gap.** No drop counter; derive from gaps > 1 s. |
| Coverage (observed free area) | Terra ticks | Per rover only; fleet sum not built. |
| Near misses, contacts | Terra summary | Exists. |
| Workload | Raw NASA-TLX on paper or a form | To prepare. |
| Score (only if NEXT match) | Zorvane scoring in sim; referee sheet on field | Out of pilot task. |

## Per-trial file set (draft)

`trials/<venue>/<operator>/<trial-index>/`: `trial.json` (labels), `argos-session-*.jsonl`, one `Terra-run-*.jsonl` per rover (or Zorvane `<run_id>.jsonl`), `tlx.csv`, `notes.md`. A trial counts as complete only when every file is present and none ends in a truncated line.

Raw logs stay out of git until the ethics path (`04-ethics-and-consent.md`) says where they may be stored.
