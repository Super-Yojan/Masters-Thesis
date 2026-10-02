# Project ARGOS — Current Project Summary

**ARGOS** is the multi-robot autonomy and human-supervision research platform. The central question is:

> **How much autonomy and information does each robot need for one human to effectively supervise a large fleet of ground robots?**

The individual rover platform is called **Terra**.

---

## 1. Overall concept

Instead of continuously sending every camera frame, point cloud, and sensor reading from every robot to one ground station, each Terra rover performs most of its computation **locally**.

The operator sees a lightweight global representation of the fleet.

A Terra normally sends things such as:

- position
- heading
- velocity
- mission status
- health/battery
- autonomy state
- attention required

rather than continuously streaming its complete perception state.

When a rover needs assistance—or the operator selects it—ARGOS can request richer information:

- occupancy grid
- point cloud
- RGB/depth
- local trajectory
- detected obstacles
- planner state

So the communication model is: **low-bandwidth awareness + high-bandwidth information on demand**.

---

## 2. Terra

**Terra** is the individual autonomous ground vehicle (`Terra-01` … `Terra-N`).

Each Terra should eventually be capable of: sensing → perception → localization → local mapping → navigation → planning → control → differential-drive rover.

The phone is intended to provide much of the rover's intelligence and sensing, while the lower-level hardware handles physical actuation.

---

## 3. Modular software architecture

Terra's robotics functionality is separated into reusable **Rust crates**:

```
terra/
├── terra-core
├── terra-math
├── terra-perception
├── terra-map
├── terra-nav
├── terra-planner
├── terra-control
├── terra-comms
├── terra-supervisor
├── terra-sim
└── terra-mobile
```

| Crate | Role |
| --- | --- |
| `terra-core` | Pose2D/3D, Velocity, Timestamp, Transform, RoverState |
| `terra-math` | Vectors, matrices, rotations, quaternions, transforms |
| `terra-perception` | Sensor-agnostic DepthFrame → point cloud → obstacle points |
| `terra-map` | Obstacle points → occupancy grid (UNKNOWN/FREE/OCCUPIED), inflation |
| `terra-nav` | Waypoints, bearing, arrival, navigation state |
| `terra-planner` | A*, DWA, trajectory generation/scoring, collision checks |
| `terra-control` | (v, ω) → wheel velocities → PID (LQR later) → PWM |
| `terra-comms` | MQTT topics (`terra/01/state`, pose, health, attention, map, …) |
| `terra-supervisor` | Attention requests, autonomy/failure/mission state, override |
| `terra-mobile` | UniFFI bindings for iOS/Swift and Android/Kotlin |

Robotics algorithms should not be rewritten per mobile platform.

---

## 4–7. Perception, depth, coordinates, intrinsics

Perception is **sensor-agnostic**: iPhone LiDAR, monocular model, or simulator all produce `DepthFrame` → `terra-perception` → point cloud → `terra-map`.

Camera projection uses intrinsics \(K\) with \(f_x, f_y, c_x, c_y\); depth pixel \((u,v)\) with \(Z=D(u,v)\) maps to camera-space \(P\).

Terra body frame convention (example): **+x forward, +y left, +z up**. Convert camera → body → world via transforms so ARKit/Android/sim conventions do not leak into navigation.

Scale intrinsics when depth resolution differs from calibration resolution; use obstacle inflation because calibration error propagates into maps.

---

## 8. Monocular depth experiment

Compare monocular predicted depth vs iPhone LiDAR on the **same RGB frame**, but judge success by **safe navigation decisions** (occupancy → DWA → trajectory), not only MAE: obstacle detection, missed/false obstacles, clearance, collisions, nav success, compute time. Metric-scale accuracy matters (relative depth alone is not enough).

---

## 9–11. Motion, DWA, planner vs controller

Unicycle/diff-drive model for sim and planner. **DWA** is the local planner (search \((v,\omega)\), simulate, reject collisions, score heading/clearance/velocity). Stack: mission → A* → DWA → PID → motors. Wheel-velocity PID first; no immediate need for LQR.

---

## 12. Levels of autonomy

1. Waypoint navigation (no autonomous obstacle handling)
2. Stop and ask (detect → stop → human attention)
3. Local avoidance (autonomous single/local obstacles)
4+. Multiple obstacles, clutter, minimal intervention

These levels are experimental variables in ARGOS.

---

## 13–15. Simulation

Start with lightweight **`terra-sim`** (2D world, geometric obstacles)—not a full 3D sim. Use MuJoCo only if dynamics matter; Unreal/3D renderer when monocular RGB/depth is the question. Final validation on the real iPhone.

---

## 16–18. Comms, supervision, attention

Local autonomy + MQTT lightweight state; detail on demand when human selects a Terra or it requests attention. ARGOS station: fleet overview, health, attention queue / priorities as \(N \to 20+\). Quest 3 / VR is a longer-term interface path.

---

## 19. Main thesis variables

Manipulate \(N\) (robots), \(A\) (autonomy), \(B\) (bandwidth), \(E\) (environment complexity), \(P \in \{\text{ground truth, LiDAR, monocular}\}\).

Measure: mission success, completion time, collisions, interventions, response time, workload, bandwidth, attention requests, navigation success.

---

## Status

Working project summary (draft). Aligns with the three-paper thesis spine: phone-as-brain feasibility, multi-phone collaborative mapping, one-human fleet dashboard.
