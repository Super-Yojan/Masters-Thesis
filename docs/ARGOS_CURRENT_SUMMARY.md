# Project ARGOS — Current Project Summary

**ARGOS — Adaptive Robotic Group Operator System** is the fleet operator layer for human supervision of autonomous robots. **Terra** is the first reference platform: a smartphone-powered, differential-drive ground rover that runs local autonomy.

The central research question is:

> **What minimum level of local autonomy is required for one human operator to effectively supervise an increasing number of robots?**

The study compares autonomy level against human cognitive load and attention scheduling for one-to-many supervision. ARGOS is platform-independent. The current master's thesis uses a homogeneous Terra fleet; heterogeneous ground, aerial, and other platforms are a longer-term direction.

This note is the working architecture and research framing. It separates the intended contract from the temporary debug path that exists today. It does not claim that every component below has been implemented or validated.

## 1. Thesis scope and autonomy levels

The primary experiment varies **fleet size × autonomy level**. Candidate fleet sizes are \(N \in \{1,2,4,8,16\}\); these are proposed conditions, not a finalized study design. Autonomy level is the second factor, \(A\).

| Level | Robot responsibility | Human responsibility |
| --- | --- | --- |
| L0 — Teleoperation | Sensing and basic state reporting | Continuous driving |
| L1 — Waypoint following | Navigate toward a commanded destination | Resolve obstacles |
| L2 — Stop and ask | Detect unsafe situations and stop | Resolve situations when requested |
| L3 — Local autonomy | Detect and locally avoid obstacles | Handle planner failures |
| L4 — Mission autonomy | Replan routes and complete missions | Handle unusual exceptions |
| L5 — Fleet autonomy | Coordinate tasks across robots | Supervise mission objectives |

The planned December defense scope primarily covers **L0–L3**. L4–L5 describe future capabilities rather than requirements for the initial thesis.

Workload and supervision metrics:

- NASA-TLX (or a similar instrument) for operator workload
- Human interventions
- Response time to an attention request
- Mission completion rate and duration, robot idle time, collisions, and navigation failures
- Communication bandwidth

Environment complexity, bandwidth, and perception source can support additional studies. The primary thesis structure remains \(N \times A\).

The three-paper spine is unchanged. Paper 1 is phone-as-brain feasibility on one Terra. Paper 2 is multi-phone collaborative mapping. Paper 3 is the ARGOS dashboard plus attention scheduling: which vehicle needs the operator, and how that load changes with \(N\) and \(A\).

## 2. Architecture split

Terra and ARGOS are separate repositories. This thesis repository holds the writing.

| Layer | Owns |
| --- | --- |
| **Terra** | Local autonomy: sensing, mapping, planning, drive, and the phone-as-brain. Reports compact perception summaries and human-attention signals. Closes the control loop onboard. |
| **ARGOS** | Fleet operator layer. High-level commands: missions, goals, and waypoints. An urgency classifier that ranks which vehicle needs human attention most. An LLM that turns operator natural language into those commands. |
| **TerraPhone VLA** | Phone-local vision-language-action, target class Gemma ~2B (or an equivalent that fits the handset). Grounds camera and language into onboard actions. This is not the operator LLM. |

ARGOS does not own sensing, local planning, the command watchdog, or the motor path. Terra does not own fleet ranking or the operator's natural-language interface. The phone VLA stays on the vehicle; the fleet LLM stays with the operator.

Code today:

- [Terra](https://github.com/Super-Yojan/Terra) — Rust robotics crates, Bevy/Avian simulator, TerraPhone (iOS, UniFFI).
- [ARGOS](https://github.com/Super-Yojan/ARGOS) — supervisor spike over the Terra Zenoh bus. See `docs/DESIGN.md` there.

### Command contract

The intended high-level contract is **go-to-waypoint** (and, more generally, missions and goals). ARGOS publishes a destination or mission; Terra's onboard stack drives there.

`cmd_vel` (`terra/rover/<id>/cmd_vel`, a twist with `linear` and `angular`) is a **temporary debug** path. The current ARGOS spike and TerraPhone use it to prove the Zenoh session and move a simulated rover. Streaming twists keeps the operator inside Terra's command watchdog and bypasses onboard autonomy. New operator features should extend supervision and high-level commands, and should leave `cmd_vel` as debug until a waypoint topic replaces it.

`fleet/size` is already the right kind of message: one fleet intent, acknowledged by `fleet/state`, with Terra deciding how to spawn and remove rovers. Mission and goal key names stay undefined until Terra specifies them.

Zenoh is the bus in both repositories today (default listen `tcp/127.0.0.1:7447`, prefix `terra/rover`). Message contracts should stay independent of the Zenoh client so a later transport change does not rewrite the autonomy code. MQTT is not the current transport.

## 3. Human attention and information flow

Human attention is the scarce resource. Robots compute locally and report lightweight state continuously:

- Robot ID, platform type, pose, and velocity
- Mission state, health, and autonomy level
- Capabilities and attention state

The communication model is **low-bandwidth continuous awareness + high-bandwidth detail on demand**. When a robot requests help or the operator selects it, ARGOS can request RGB/depth, point clouds, local occupancy maps, trajectories, obstacles, and planner diagnostics. Always-on raw video is outside the default path.

Terra publishes perception summaries and explicit attention signals (stuck, obstacle, lost localization, battery, watchdog, and similar), with severity and whether the robot can safely wait. ARGOS ingests those signals and runs an **urgency classifier** that ranks which vehicle needs the operator now. The station should answer four things: what the fleet is doing, which robots need help, why, and what action the operator can take.

Operator natural language becomes structured commands (go to, mission, stop, inspect) through the ARGOS LLM. High-risk actions stay human-in-the-loop. Phone-local VLA may ground a scene into an onboard action; it does not replace the fleet ranker.

## 4. Terra and cross-platform software

Terra's stack is sensing → perception → localization → local mapping → navigation → planning → control → differential-drive actuation.

A smartphone supplies sensing and compute (the phone-as-brain). TerraPhone handles sensor access, permissions, device lifecycle, UI, and hardware adapters. Reusable Rust libraries hold the robotics algorithms so the same code can run in simulation, on iOS, and later on Android and physical vehicles. UniFFI is the binding TerraPhone uses today.

Crates in the Terra repository now:

| Crate | Responsibility today |
| --- | --- |
| `terra-types` | Sensor samples, coordinate conventions, commands, motor outputs |
| `terra-state` | VIO velocity anchors with bounded IMU prediction |
| `terra-mapping` | Rolling local occupancy grids from depth and camera poses |
| `terra-control` | Differential-drive velocity control, feedforward, anti-windup, freshness checks |
| `terra-transport` | Leased Zenoh publishing. Today this is the debug `cmd_vel` path |
| `terra-mobile` | UniFFI interface shared by Swift and Rust |

Intended library boundaries, including work that is not a crate yet:

| Library | Responsibility |
| --- | --- |
| `terra-perception` | Sensor-agnostic depth → point cloud → obstacle points |
| `terra-nav` | Waypoints, goal distance and bearing, arrival, route progress |
| `terra-planner` | Local trajectories, collision checks, DWA, later global planning |
| `terra-control` | Desired motion → wheel targets → motor control |

Shared supervision stays in ARGOS. Wheel geometry, PWM, and differential-drive equations stay in Terra.

## 5. Perception, geometry, and mapping

Perception is **sensor-agnostic**. iPhone LiDAR, a monocular model, or the simulator produces a depth frame that flows through mapping into an occupancy grid.

For camera intrinsics \(f_x,f_y,c_x,c_y\) and depth \(Z=D(u,v)\), camera-space projection is:

\[
X=\frac{(u-c_x)Z}{f_x}, \qquad
Y=\frac{(v-c_y)Z}{f_y}.
\]

Scale intrinsics when depth resolution differs from calibration resolution. Terra's body frame is **+x forward, +y left, +z up**. Convert sensor → body → world explicitly so mobile OS and simulator conventions do not leak into navigation:

\[
P_{world}=T_{world\leftarrow body}T_{body\leftarrow sensor}P_{sensor}.
\]

Calibration uncertainty affects obstacle locations. Occupancy mapping should account for vehicle size and a safety margin through obstacle inflation.

The monocular-depth research track compares predicted depth with iPhone LiDAR on the same RGB frame, and can use simulator ground truth as a separate reference condition. Evaluate **navigation consequences**, alongside depth error: obstacle recall, false obstacles, minimum clearance, collisions, mission success, and compute latency. Metric-scale accuracy matters; relative depth alone is insufficient for metric navigation.

## 6. Navigation, planning, and control

Use a unicycle/differential-drive model for local planning. **DWA — Dynamic Window Approach** searches reachable \((v,\omega)\) commands, predicts trajectories, rejects collisions, and scores heading, clearance, and forward progress.

Waypoint following and stop-and-ask are the lower-autonomy conditions. DWA supplies local obstacle avoidance for L3. Global planning such as A* can be added when route replanning is the question.

Intended command path:

```text
ARGOS mission / goal / waypoint → Terra local planner (DWA) → wheel targets → motors
```

Debug path, temporary:

```text
operator or TerraPhone → Zenoh cmd_vel → simulator velocity loop
```

The planner chooses desired motion; the controller makes the rover follow it. Start with wheel-velocity control of the kind already in `terra-control`. Introduce LQR or MPC only to solve a demonstrated problem.

## 7. Simulation, tiles, and hardware

**Simulation fidelity follows the research question.**

- The current rover simulator is Bevy/Avian: fleet spawning, cameras, occupancy, and Zenoh. It is the integration target for phone and ARGOS spikes.
- A lightweight 2D simulator (poses, goals, geometric obstacles, collision, simulation time) remains appropriate when the question is repeatable navigation and fleet counts rather than rendering.
- Use a physics simulator when friction, slip, inertia, slopes, or motor dynamics are the question.
- Use a visual simulator when the question is RGB perception, monocular depth, lighting, or visual domain shift.
- Validate on physical Terra hardware, including the real phone sensing pipeline.

Higher-fidelity simulators are supporting tools. They are not prerequisites for the core human-supervision experiment.

Near-term simulator and hardware work, tracked on Terra:

- [Terra #9](https://github.com/Super-Yojan/Terra/issues/9) — real-world Bevy tiles via [bevytiles](https://docs.rs/bevytiles/latest/bevytiles/), plus the ARGOS go-to-waypoint contract. `cmd_vel` stays debug-only.
- [Terra #10](https://github.com/Super-Yojan/Terra/issues/10) — TerraPhone to the real chassis over Bluetooth (command, telemetry, loss-of-link stop). Zenoh remains the sim and fleet bus. ARGOS-over-Bluetooth is out of scope.

## 8. ARGOS station

`argos-station` should provide fleet status, robot health and mission state, the urgency ranking, and actionable robot detail on selection. Situational awareness and response to attention requests come before a 3D view.

Operator language maps to validated high-level commands. The urgency classifier, that language path, and the attention contract are [ARGOS #2](https://github.com/Super-Yojan/ARGOS/issues/2). Terra's matching publisher is [Terra #11](https://github.com/Super-Yojan/Terra/issues/11). On-device VLA for TerraPhone is [Terra #12](https://github.com/Super-Yojan/Terra/issues/12).

A 3D or Quest 3 / VR interface is a longer-term path. Mission-level objectives, capability matching, heterogeneous fleets, and fleet task allocation are also future directions. The station still talks to robots through capabilities (waypoint navigation, obstacle detection, local mapping), not through wheel radius or PWM.

## 9. Experiment engineering

Instrument the system from the beginning. Log mission start and completion, goal reached, collisions, attention requests and responses, the rank the classifier assigned, human interventions, planner and localization failures, stops, and resumes. Each event needs a timestamp and a robot ID.

Record fleet size \(N\), autonomy level \(A\), environment, random seed, duration, and software versions with the logs. Experiments should be repeatable and traceable to their conditions.

Use explicit package interfaces, documented coordinate conventions, and SI units internally where practical. Validate core algorithms with automated tests and navigation behaviors with scenario-level regression tests before hardware validation.

## 10. Near-term priorities and success criteria

1. **Waypoint contract.** Terra accepts a go-to-waypoint (Terra #9). ARGOS sends it. `cmd_vel` remains debug.
2. **One Terra, then a fleet.** Simulated waypoint navigation, obstacle detection, stop-and-ask, and local avoidance, then several Terras with independent missions on one bus.
3. **Attention scheduling.** Terra emits perception and attention reports (Terra #11). ARGOS ranks them and can turn operator language into a high-level command (ARGOS #2).
4. **Phone and hardware.** On-device VLA on TerraPhone (Terra #12). Bluetooth to the chassis (Terra #10) when a physical demo is the question.
5. **Freeze experimental features** once the \(N \times A\) study can run. Prioritize data collection, analysis, writing, and validation.

Short-term success: one operator supervises multiple simulated Terras at different autonomy levels, and ARGOS measures workload and fleet performance, including which robot was scheduled for attention.

Medium-term success: the same Terra autonomy software runs on physical ground vehicles, with interchangeable perception sources. Long-term success: ARGOS supervises heterogeneous fleets from mission intent, through capability matching rather than a Terra-only command set.

## Status

Working project summary. The thesis priority is scalable human supervision: autonomy level against cognitive load and attention scheduling. The three-paper spine still holds; Paper 3 is the ARGOS dashboard and attention scheduler. Phone-as-brain feasibility, collaborative mapping, monocular perception, and heterogeneous fleets remain the other papers or later directions. They are not all prerequisites for the first \(N \times A\) experiment.

Open implementation notes: [Terra #9](https://github.com/Super-Yojan/Terra/issues/9), [#10](https://github.com/Super-Yojan/Terra/issues/10), [#11](https://github.com/Super-Yojan/Terra/issues/11), [#12](https://github.com/Super-Yojan/Terra/issues/12), and [ARGOS #2](https://github.com/Super-Yojan/ARGOS/issues/2).
