# ARGOS, Terra, and Zorvane current project summary

Updated 2026-10-18. This repository holds thesis writing and research records; application code lives in the three platform repositories.

## Platform ownership

| Repository | Current role |
| --- | --- |
| [ARGOS](https://github.com/Super-Yojan/ARGOS) | Browser operator interface in React, backed by a Rust Axum server connected to Zenoh. The native Swift station is a legacy fallback; Unity is a historical prototype. |
| [Terra](https://github.com/Super-Yojan/Terra) | Vehicle runtime: portable Rust sensing, mapping, navigation, autonomy, control, transport, and mobile bindings. TerraPhone remains the iOS vehicle application. |
| [Zorvane](https://github.com/Super-Yojan/Zorvane) | Bevy/Avian world and competition simulator, cameras, physics, browser simulation, and Zenoh integration. It consumes a pinned revision of Terra's shared robotics crates. |
| Masters-Thesis | Paper drafts, thesis outline, proposed study design, and experiment records. |

The fleet supervisor sends intent; Terra retains onboard motion authority, command freshness checks, and safety arbitration. The browser reaches the ARGOS server, which communicates with the robot or simulator through Zenoh. Running the browser simulator through its student-client pairing gateway is a separate workflow from running the ARGOS operator interface.

## Implemented contracts and remaining boundaries

ARGOS's browser path supports authenticated operator claims, waypoint send/cancel, arm/disarm, autonomy selection, navigation geometry and tuning, observed occupancy-map display, held manual driving after explicit takeover, and a latched emergency stop. Consult the [ARGOS README](https://github.com/Super-Yojan/ARGOS/blob/main/README.md) for current startup and manual-control behavior.

Waypoints are implemented; they are no longer a topic awaiting design. The `terra/rover/<id>/goal` contract coexists with ARGOS operator input on `terra/rover/<id>/teleop`, which carries authority and ordering information. The separate `terra/rover/<id>/cmd_vel` path is used for direct simulator/phone drive. Browser manual driving requires fresh armed hardware and explicit takeover; release, lost focus, or lost control stops held input. Emergency stop latches vehicle safety and requests disarm; resetting that safety latch currently requires the native operator application. These controls have automated test coverage, but physical end-to-end driving and stop validation remain pending. Fleet sizing uses `terra/rover/fleet/size` and `terra/rover/fleet/state`.

Terra has navigation, waypoint, autonomy, mapping, state, control, transport, experiment, and mobile crates. A* waypoint routing and L4 target-search work already exist. The [L4 implementation record](superpowers/plans/2026-10-08-l4-target-search.md) distinguishes deterministic simulator evidence from outstanding rendered scenario comparisons and physical detector/hardware validation. Do not treat a merged implementation or a simulator success as a completed human-subject experiment or physical deployment result.

Autonomy names in runtime messages and labels in an early research taxonomy are not interchangeable. Use the runtime contract for commands and record the exact software revision and behavior used in each study condition.

Zorvane pins Terra dependencies in its [Cargo.toml](https://github.com/Super-Yojan/Zorvane/blob/main/Cargo.toml). New Terra work is not automatically available in the simulator until that pin is updated and integration is validated. Local GMU/shared-world experiments are separate from released main-branch behavior.

## Research scope

The central question remains: **What minimum level of local autonomy allows one human to supervise an increasing number of robots effectively?** The proposed primary factors are fleet size and autonomy level. Candidate fleet sizes, workload instruments, and a defense schedule in older notes are planning assumptions, not a finalized protocol or completed results.

The three-paper spine remains:

1. Phone-as-brain feasibility on a single Terra.
2. Collaborative mapping and multi-phone SLAM.
3. ARGOS supervision, human workload, and attention scheduling.

Track interventions, response latency, mission success and duration, idle time, collisions, navigation failures, and bandwidth alongside operator workload. Record random seeds, environment, autonomy behavior, fleet size, timestamps, robot IDs, and software versions. Attention scheduling, operator language interpretation, physical perception, and heterogeneous fleets require their own evidence; the existence of browser controls does not establish their validation.

## Current work and historical records

Use each platform's main-branch documentation and linked PR evidence for implementation status. Terra's mounting, frontier exploration, Android, and offline VLM evaluation work have independent acceptance boundaries; Android support does not replace the iOS vehicle runtime, and offline VLM evaluation does not establish an onboard action policy.

The [early architecture summary](archive/ARGOS_EARLY_ARCHITECTURE.md) preserves the original geometry, DWA, information-flow, and study framing. Its references to a supervisor spike, future waypoint contract, simulator inside Terra, and open implementation priorities are historical. Existing paper drafts and recorded experiments are preserved; they should be revised through the research process rather than silently rewritten to match application development.
