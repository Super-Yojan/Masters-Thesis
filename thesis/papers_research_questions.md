# Three-paper thesis spine

Shared platform: consumer phone as sensor/brain on a cheap differential-drive chassis for multi-robot disaster-recovery (and related) fleets. Same stack across all three papers; autonomy-level ladder links them.

**Terra** is local autonomy (sensing, mapping, planning, drive, phone-as-brain) and reports perception plus human-attention signals. **ARGOS** is the fleet operator layer: high-level commands (missions, goals, waypoints), an urgency classifier that schedules which vehicle needs the operator most, and an LLM from operator language to those commands. A phone-local VLA (Gemma ~2B class) on TerraPhone is onboard grounding, separate from the operator LLM. The study compares autonomy level \(A\) with cognitive load for one-to-many supervision as fleet size \(N\) grows. Architecture detail is in [`docs/ARGOS_CURRENT_SUMMARY.md`](../docs/ARGOS_CURRENT_SUMMARY.md).

## Paper 1 — Phone-as-brain feasibility

**Research question:** Can a consumer phone (app + cameras/IMU/compute) run the sensing and control loop for a cheap differential-drive rover well enough for waypoint navigation with local obstacle avoidance, without onboard industrial compute?

**Metrics:**
- Control/sensing loop rate and end-to-end latency
- Waypoint navigation success rate
- Obstacle clearance / collision rate
- Human interventions or emergency stops per run
- Power draw and thermal throttling limits
- Cost and setup time vs a dedicated-compute baseline

## Paper 2 — Multi-phone collaborative SLAM / shared maps

**Research question:** How well can multiple phone-mounted rovers build and fuse a shared map (pose + occupancy or sparse landmarks) under limited bandwidth and noisy depth, compared with single-robot mapping?

**Metrics:**
- Map completeness / coverage
- Absolute and relative localization error
- Merge consistency in overlap regions
- Bandwidth and compute per phone
- Time to a usable shared map
- Robustness under lost robots or network dropouts

## Paper 3 — Dashboard and attention scheduling (ARGOS)

**Research question:** What dashboard and attention scheduler let one operator supervise \(N\) phone-brain rovers as onboard autonomy \(A\) increases from “sense and stop” to “avoid and continue,” and which vehicle should receive human attention first?

**Metrics:**
- Maximum fleet size at fixed operator workload
- Interventions per robot-hour
- Operator response time to “attention needed”
- Task success rate
- NASA-TLX (or similar) workload scores
- Interface error rate (wrong robot selected, missed alerts)
- Whether the urgency ranking matched the robot that actually needed help

## Thesis glue

Same chassis/phone stack for all three papers. Factors are fleet size \(N\) and autonomy level \(A\). Workload is NASA-TLX, interventions, and response time to attention. Paper 3 evaluates the ARGOS dashboard and attention scheduler on top of the autonomy levels demonstrated in papers 1–2.
