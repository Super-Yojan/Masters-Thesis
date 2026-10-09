# L4 Target Search Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task by task after implementation is requested. Steps use checkboxes for tracking.

**Goal:** A rover accepts a bounded target-search request, explores autonomously, confirms a requested target from observations, and reports completion while preserving takeover and common safety.

**Architecture:** A portable search controller in `terra-autonomy` selects navigation goals and consumes normalized detector observations. The existing arbiter remains the sole motion authority, composing the waypoint follower and local planner. Platform adapters provide observations; simulator hidden truth belongs only to the observation generator and evaluation layer.

**Tech Stack:** Existing Rust 2024 workspace, serde, Zenoh, UniFFI and Swift; Zorvane for simulation. No new inference framework is required for the first simulator milestone.

**Spec:** User clarification on 2026-10-08: “Target search: explore, detect a requested target, and report completion.” Existing references: `Terra/docs/DASHBOARD_TAILSCALE.md`, `Terra/docs/autonomy/PROTOCOL.md`, `Terra/docs/superpowers/plans/2026-10-06-level-of-autonomy.md`. Paths below are relative to Terra unless explicitly marked Zorvane or ARGOS.

## Baseline and scope

Inspected Terra HEAD `a059a27` and its working tree. Existing `Level` variants are `Teleop`, `AssistedTeleop`, `Waypoint`, and `Supervised`; supervised exploration proposes frontiers for human approval. `terra-navigation::frontier` searches the current rolling map. `terra-experiment::Mission` stores simulator survivor truth and records sightings/reports; it is an evaluator, not an onboard detector or search policy. Dashboard L4 is presently unavailable. The thesis summary uses a different numbering scheme; retain named protocol levels and document this distinction.

Terra has substantial concurrent uncommitted mobile/transport work. Reinspect interfaces and isolate implementation before editing; do not reset or overwrite these changes. The simulator source has moved to Zorvane; the local `simulator/` contains build artifacts and must not be treated as source.

First release: one requested target class, first confirmed instance, one rover, bounded rectangular local-world search area, finite time budget. Success means a confirmed target report with estimated position and evidence; return-to-base, multi-target completion, fleet allocation, arbitrary natural-language grounding and VLA are separate extensions. Simulator completion does not establish physical recognition capability.

## Global constraints

- Reuse shared collision admissibility, freshness checks, controller limits and emergency-stop latch. Search never writes motor output directly.
- Protocol names remain `teleop`, `assisted_teleop`, `waypoint`, `supervised`; add `target_search` without changing their meaning.
- World frame is +x forward, +y left, +z up; use SI units and local monotonic time. WGS84 search polygons are deferred.
- Unknown or out-of-map cells are not certified free. Constrain the entire inflated rover footprint to the search boundary.
- Planner/configuration and target-confirmation settings are fixed and recorded per experiment run.
- Only platform-observed detections reach the search policy; hidden target lists and evaluator `Mission::candidates()` never do.
- Initial proposed detector gate: confidence >=0.8, three distinct frames spanning >=0.5 seconds, position agreement <=1 metre, observation receive age <=0.5 seconds. These are configurable engineering defaults requiring calibration, not validated physical thresholds.
- A confirmed report is terminal locally; delivery acknowledgements are separate. Do not resume searching after completion, reconnection, reset or mode reselection.

## Review focus

1. Delayed or duplicate observations must not confirm a target in another search session (Task 3).
2. A rolling map revisiting the same frontier must not create an endless search or falsely prove complete area coverage (Task 2).
3. A dynamic obstacle blocking a chosen route must trigger bounded recovery followed by an explicit attention hold (Tasks 2 and 4).
4. Cancellation, takeover and emergency stop concurrent with detection must prevent motion and cannot resurrect prior intent (Task 4).
5. Lost connection or unavailable detector must not produce false success or advertise an unsupported L4 capability (Tasks 5–7).

## Task 1: Versioned search contract

**Files:** Modify `crates/terra-autonomy/src/{contract,lib}.rs`, `crates/terra-autonomy/tests/contract.rs`, `docs/autonomy/PROTOCOL.md`; create `crates/terra-autonomy/src/search_contract.rs`.

**Interfaces:** Export `SearchRequest { version: u32, run_id: String, search_id: String, token: String, target_class: String, bounds: SearchBounds, time_budget_s: f64 }`, `SearchBounds { min_x: f64, min_y: f64, max_x: f64, max_y: f64 }`; `SearchActionRequest` carries version/run/search/token and `Pause | Resume | Cancel`; `SearchStatus` carries IDs, revision, phase, reason, elapsed time, active goal, optional confirmed report and capability. Export `decode_search_request(&[u8]) -> Option<SearchRequest>` and `decode_search_action(&[u8]) -> Option<SearchActionRequest>`.

- [ ] Add failing serialization/validation tests: version=1; existing token rules; target class 1–64 ASCII letters/digits/underscore/hyphen; finite ordered bounds; each side <=100 metres; 0 < budget <=3600 seconds; <=2048-byte commands. Reject unknown fields, wrong versions, invalid IDs and nonfinite geometry.
- [ ] Run `cargo test -p terra-autonomy --test contract`; confirm new cases fail before implementation.
- [ ] Add `Level::TargetSearch`, named serialization, records, codecs and protocol topics `/search`, `/search/action`, `/search/status`, `/search/report`, `/search/report/ack` under `terra/rover/<id>`.
- [ ] Define accepted/rejected command receipt in search status, token idempotence and conflicting-token rejection. A request is accepted only in selected target-search mode with fresh required inputs and detector capability; one active search per rover, reject replacement until cancelled. Mode selection alone creates no search intent.
- [ ] Re-run contract tests and commit the contract/docs together.

## Task 2: Bounded exploration with route memory

**Files:** Create `crates/terra-navigation/src/search.rs` and `crates/terra-navigation/tests/search.rs`; modify `crates/terra-navigation/src/lib.rs`.

**Interfaces:** `SearchNavigator::new(bounds: SearchBounds, config: SearchNavigationConfig) -> Result<Self, SearchNavigationError>`; navigation owns its geometry type, with autonomy converting contract bounds. `next_goal(&mut self, map: &MapSnapshot, pose: Pose, map_revision: u64, now: f64) -> SearchNavigationDecision`; `record_progress(&mut self, pose: Pose, now: f64)`; `invalidate_goal(&mut self, now: f64)`. Decisions are `Goal { x, y }`, `Exhausted`, or `Blocked { reason }`. Reuse existing `Pose`, `frontier`, `reachable` and local planner.

- [ ] Write deterministic tests for boundary footprint containment, revisited frontiers, map origin shifts, blocked routes, no reachable frontier and a U-shaped obstacle requiring intermediate goals.
- [ ] Run `cargo test -p terra-navigation --test search`; confirm failures.
- [ ] Implement mission-scoped observed-cell memory at fixed initial map resolution, bounded to 250,000 cells. Do not replace newer occupancy with stale data; reset on frame/resolution incompatibility with an explicit hold. Persist visited/failed frontier positions across rolling-map shifts.
- [ ] Use deterministic four-neighbour A* through footprint-inflated observed free cells to frontier vantages; supply intermediate goals to the existing local planner. Stop segment advance when changed occupancy invalidates its route; never route through unknown cells.
- [ ] Proposed recovery defaults: progress of >=0.25 metres resets a 10-second stuck timer; exclude failed goal for 30 seconds; at most three failed routes before `Blocked`. Exhaustion means no currently reachable unexplored vantage, not proof that the target is absent.
- [ ] Re-run navigation tests and commit.

## Task 3: Observation-based confirmation and search lifecycle

**Files:** Create `crates/terra-autonomy/src/search.rs`, `crates/terra-autonomy/tests/search.rs`; modify `crates/terra-autonomy/src/lib.rs`.

**Interfaces:** `TargetObservation { run_id, search_id, frame_id, target_class, confidence, world_x, world_y, received_at, evidence_id }`; IDs/class use the contract rules. `SearchController::start(request: SearchRequest, now: f64) -> Result<Self, SearchError>`; `observe(&mut self, observation: TargetObservation, now: f64) -> Result<(), SearchError>`; `tick(&mut self, input: SearchInput<'_>) -> SearchDecision`. `SearchInput` contains monotonic time, pose/map/revision and detector health; decisions are navigate, hold or terminal report. `SearchReport` contains stable report ID, run/search IDs, target class, estimated world position, confirmation time and contributing frame/evidence IDs.

- [ ] Test a matching three-frame candidate confirms once; wrong class, repeated frame, stale/out-of-order time, low confidence, inconsistent position and foreign run/search IDs never confirm. Bound retained candidates/evidence to 64 observations and reject frame IDs older than the accepted stream position.
- [ ] Test pause freezes navigation but elapsed budget continues; cancel is terminal; timeout yields `timed_out`; no frontier yields `exhausted`; detector loss yields `needs_attention`; every terminal state emits zero motion intent.
- [ ] Run `cargo test -p terra-autonomy --test search`; confirm failures.
- [ ] Implement `Searching -> Confirming -> Completed`, with `Paused`, `NeedsAttention`, `Cancelled`, `TimedOut` and `Exhausted`. Slow/stop while confirming using the common planner; completion does not require approaching/touching the target. Calculate position from accepted observations, never evaluator coordinates.
- [ ] Re-run search tests and commit.

## Task 4: Integrate the sole motion arbiter

**Files:** Modify `crates/terra-autonomy/src/arbiter.rs` and `crates/terra-autonomy/tests/arbiter.rs`.

**Interfaces:** Add `start_search(request: SearchRequest, now: f64) -> Result<(), SearchError>`, `apply_search_action(request: SearchActionRequest, now: f64) -> Result<(), SearchError>`, `accept_target_observation(observation: TargetObservation, now: f64) -> Result<(), SearchError>` and optional search status/report to `ArbiterOutput`. Detector availability is a capability supplied by adapters; do not infer it from a healthy map.

- [ ] Add failing matrix tests for target-search intent through follower/DWA; missing map/pose/detector; bounded recovery; safety stop during confirmation; explicit takeover; cancellation with queued observations; mode change/reset; duplicate start/action; per-rover isolation.
- [ ] Run `cargo test -p terra-autonomy --test arbiter`; confirm failures.
- [ ] Compose the search controller inside the arbiter. Search-generated goals bypass supervised proposal approval but never safety/planner validation. Existing supervised behavior remains approval-based. Operator `/goal` during target search is rejected with `search_active`; redirect requires cancel and fresh intent.
- [ ] Mode change or e-stop cancels search and clears its goals/observations. Healthy reset holds until a fresh request. Pause clears motion; explicit resume revalidates inputs and selects a fresh route. Terminal reports cannot be overwritten by delayed ticks.
- [ ] Run `cargo test -p terra-autonomy -p terra-navigation -p terra-control -p terra-waypoint`; commit.

## Task 5: Transport, reporting and experiment records

**Files:** Modify `crates/terra-transport/src/control_plane.rs`, `crates/terra-transport/src/lib.rs`, `crates/terra-experiment/src/lib.rs`, `crates/terra-experiment/src/metrics.rs`; create `crates/terra-transport/tests/search.rs`, `crates/terra-experiment/tests/search.rs`.

**Interfaces:** Adapter command dispatch passes decoded search commands to Task 4. Status is authoritative and periodically republished; report acknowledgement contains version/run/search/report/token. Shared events: search accepted/paused/resumed/cancelled, route selected/failed, candidate observed/rejected, target confirmed, report published/acknowledged, search terminal and attention requested.

- [ ] Test malformed/oversized search messages, duplicate tokens, report retry after reconnect, foreign acknowledgement, queue overload with stop priority and status replay for late subscribers.
- [ ] Test a synthetic run derives time to confirmation, outcome, routes failed and interventions; missing detection capability remains unavailable; exhausted/timed-out searches never count as success.
- [ ] Run the new package tests before implementation and observe failure.
- [ ] Extend existing bounded control queues and recording. Retain at most 128 unacknowledged terminal reports; republish every second until acknowledgement/run close. Queue overflow holds search with a delivery/logging fault rather than discarding a success record silently. Acknowledgement never changes local confirmed outcome.
- [ ] Record detector ID/version, thresholds, observation provenance, navigation limits, seed, revisions and software versions in the manifest. Derive recall/false-positive metrics only using evaluator truth outside onboard policy.
- [ ] Run `cargo test -p terra-transport -p terra-experiment`; commit.

## Task 6: Simulator milestone and acceptance scenarios

**Repository:** Zorvane. Source paths below are those documented by Terra's existing plan and must be verified against a fetched checkout before execution.

**Files:** Modify `simulator/src/{autonomy,mission,zenoh_bridge,experiment}.rs`; add scenario fixtures and search integration tests in that repository.

**Interfaces:** Observation adapter emits Task 3 observations only after range, field-of-view and per-target occlusion checks. Planner sees depth-derived maps and observations only. Evaluator alone reads survivor placements. First supported class: `survivor`; other classes are rejected explicitly.

- [ ] Add failing seeded tests: visible target found; occluded target not observed until visible; wrong class ignored; unreachable target exhausted; blocked route recovered; budget exceeded; stop/takeover during confirmation; two independent rover requests.
- [ ] Wire a deterministic simulated observation adapter using configurable false-positive/false-negative fixtures. Avoid feeding a single global line-of-sight boolean to all targets. Connect search commands and reporting to the shared arbiter; no simulator motion shortcut.
- [ ] Demonstrate one complete search without frontier approvals or manual reports and an alternate-route scenario beyond L3 local avoidance. Save input trace, manifest and output events.
- [ ] Run `cargo test -p zorvane` in the verified checkout. Compare fixed seed/config with supervised exploration; report success, false confirmations, intervention count, search time and collisions separately.
- [ ] Commit simulator changes; mark simulator-only detection capability in evidence.

## Task 7: Phone bindings and operator interface

**Files:** Modify `crates/terra-mobile/src/autonomy.rs`, `crates/terra-mobile/src/lib.rs`, `mobile/ios/TerraPhone/PhoneController.swift`, `mobile/ios/TerraPhone/ContentView.swift`; create `crates/terra-mobile/tests/search.rs`; update `docs/DASHBOARD_TAILSCALE.md`. ARGOS/dashboard source location requires discovery before its companion implementation plan is finalized.

**Interfaces:** UniFFI exposes typed search request/action/status/report records and normalized observation ingress. UI uses confirmed `supported_levels` and detector capability. Operator specifies a target class, area and budget; selects search; sees phase, candidate/confirmed evidence, terminal outcome and pause/resume/cancel/takeover/stop.

- [ ] Test bindings replay the same traces as Rust; simulator remote-control mode sends requests without running a second arbiter. Test unsupported physical detector keeps L4 unavailable; no optimistic successful mode/start display.
- [ ] Implement bindings and regenerate with existing project tooling. Add detector-adapter registration with explicit class/version capabilities. Physical inference is a separate selected-model deliverable: capability remains unavailable until calibrated observation production passes the same contract tests.
- [ ] Add search controls in the existing native operator surface and a companion plan for the verified dashboard source. Test late status, reconnect, rejected commands, terminal report evidence and stale acknowledgements.
- [ ] Run mobile Rust tests, existing Swift smoke checks and binding builds; record actual device tests separately. Commit.

## Task 8: Release evidence and compatibility

**Files:** Modify `docs/autonomy/evidence/README.md`, `docs/autonomy/PROTOCOL.md`, `docs/crates/terra-autonomy.md`, `docs/DASHBOARD_TAILSCALE.md`; add `tests/fixtures/autonomy/search/` input/output traces.

- [ ] Run `cargo test --workspace` in Terra and the Task 6 simulator checks after integration. Existing mode/goal/proposal fixtures must still pass.
- [ ] Verify portable replay and adapters produce matching search state, selected navigation intent and exactly-once completion events from identical normalized inputs.
- [ ] Check old clients tolerate unknown named levels; if they do not, update clients before enabling `target_search` advertisement. Do not map L4 onto the old `supervised` value.
- [ ] Publish an acceptance table for contracts, safety, navigation, observation isolation, completion/reporting, logging, simulator and phone. Distinguish implemented, simulator validated, physical detector unavailable and hardware validated.
- [ ] Commit docs/evidence. Keep thesis L0–L3 baseline scope intact unless the research protocol is separately revised.

## Delivery order and completion gate

Suggested review units: (1) contract + exploration + confirmation + arbiter; (2) transport/logging + simulator acceptance; (3) bindings/operator controls + evidence. No L4 availability claim until a platform can accept a request, explore without per-frontier approval, confirm sensor-observed targets, report completion and obey takeover/stop in scenario tests.

Design decisions for review: bounded local search area, first-instance completion, simulator survivor detector first, configurable confirmation defaults, and physical detector availability as a separate gate. This plan does not select or benchmark a real camera recognition model.

## Implementation handoff — 2026-10-08

Implemented the contract, observed-map routing, confirmation state machine, sole-arbiter integration, transport/report receipts, metrics, typed mobile bindings, phone/ARGOS controls, and Zorvane detector integration. Source: `/Users/yojan/git/Terra`, `/Users/yojan/git/ARGOS`, `/Users/yojan/git/Zorvane`.

Terra and ARGOS workspace tests pass. TerraPhone simulator build and binding smoke pass. Zorvane compiles; a deterministic headless replay confirms a survivor and stops, with detector range/FOV/occlusion tests passing. Evidence is in Terra `docs/autonomy/evidence/l4/`. Review found four defects; fixes have regression coverage.

Release validation still outstanding: rendered multi-rover scenario matrix, fixed-seed comparison with L3, false-positive/negative calibration, physical detector and hardware trials. Full Bevy test compilation exceeded available disk. Desktop Xcode build requires unrestricted Swift macro execution; its final verification is recorded in the execution ledger. No commits or deployment performed.
