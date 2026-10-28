# Experiment results (as of 2026-10-28)

One place for every experiment result, graph and picture so far. `index.html` is the same page as the
private artifact (https://claude.ai/artifact/QrxvjBk4Luk6PXGGhtanLM) with figures linked from `figures/`.
Field screenshots with map imagery are only in the artifact, not here. Numbers are copied from the
analyses in Ch6, the phone paper (papers/paper1-phone-as-brain) and the project notes; nothing is re-estimated.

## Scoreboard

| Experiment | Date | Headline result | Verdict |
| --- | --- | --- | --- |
| E1 VIO speed vs OptiTrack | Oct 26–27 | Phone reads 0.912× true speed (s.d. 0.065, 16 runs; one more at 0.60); bias, noise, delay, heading pass | Fail (R1 scale) |
| E2 Sensor timing on phone | Oct 27 | Debug: 233 stale ticks (1.8%), all Terra queue. Release: 0 | Pass in Release |
| Occupancy false obstacles | Oct 25–26 | Classifier floor plane tilted ~16° → far floor marked obstacle | Fixed (Terra #66, #68) |
| terra-mini route loss | Oct 26 | A* reach 0.297 m needed a 0.5 m gap; doorway at that width | Fixed (Terra #72) |
| YOLO bucket detector, Zorvane | Oct 27 | Ground <10 m: 21/22 blue sunlit, 5/18 orange shaded; stands 3/17; 0 false (noon) | Mixed |
| Outdoor session d45c20e5 | Oct 27 | ~45 stale_imu trips in 50 s, 128 motor toggles; GPS age median 3.3 s (limit 3.0), accuracy 12.8 m | Open |
| Glass barrier | Oct 27 | Mesh barrier did not stop rays on real glass | Parked |
| Two-rover map fusion self-test | Oct 26 | Rotated cases 3 cm off; translation case 0.199 m off (tol. 0.30 m) | Mixed |
| E1b, E3 depth, E5 GNSS, E6 endurance | – | Not run | Pending |

## E1 VIO speed vs OptiTrack

| Req. | Threshold | Measured | Verdict |
| --- | --- | --- | --- |
| R1 scale | 0.97–1.03 | Mean 0.912, s.d. 0.065 (16 runs); 1 run 0.60; all 17 mean 0.894, median 0.92 | Fail |
| R1 bias | ≤ 0.01 m/s | 0.0009 m/s, s.d. 0.003 at rest | Pass |
| R2 noise | ≤ 0.02 m/s | 0.007 in band, 0.012 above | Pass |
| R3 delay | < 382 ms | ~50–70 ms vs gyro | Pass |
| R4 heading | < 30° | within 0.1° over a 475° arc | Pass |

Sessions: S1 (Oct 26) 0.98 and 0.81; S2 0.81/0.89/0.93/0.88 (mean 0.88); hand carry 4.06/4.42 m = 0.92;
S3 ~1.0 (1 run); S4 (Oct 27) 10 runs 0.83–1.01, mean 0.92, outlier 0.60. OptiTrack checked with a 3 m tape (0.01 m off).
Arc yaw rate was blind (flat-phone IMU path, fixed Terra #74); 2.75 m VIO position jump on the S1 arc.
Data: `data/vio_session1_summary.json`.

## E2 Sensor timing (Terra PR #89 probe)

`data/sensor_timing_summary.csv` holds all four runs. Debug 336 s: queue wait p99 2414 ms, tick rate 39 Hz,
depth→map p50 66 ms, 233 stale ticks at the 0.1 s gate. Release (122/52/38 s): 0 stale ticks, ticks 96–100 Hz,
depth→map p50 9–16 ms. iOS IMU delivery p99 ~2 ms in every run. iOS stalls: 1.17 s at ARSession start, 2.3 s at 311 s (Debug, thermal 2).

## Occupancy map tilt (point captures)

- argos-75eca1f97bcb (Oct 25): plane normal [-0.133, 0.234, 0.963] = 15.6° tilt; floor red 0% at 1–1.5 m, 60% at 3–3.5 m, 100% beyond 3.5 m. Labels free 70,084 / obstacle 208,266 / overhead 127,565.
- argos-b0eca906a40d: HorizonBand, band range 2.84 m (nominal 0.5 m height) vs camera ~0.4 m; 45% of red within 8 cm of floor.
- argos-f03552358254 (mocap room): band range 1.30 m; all 4,094 obstacle points were floor in a 1.1–1.3 m ring.

## Bucket detector in Zorvane

See `data/bucket_sim_README.md` for the full table and method.

## Figures

| File | What it shows |
| --- | --- |
| vio_scale_ratios.png | Phone/OptiTrack speed ratio per run by session, R1 band |
| vio_B_v0.3_r2.png | S1 run 2: loop holds phone 0.30, true ~0.37 m/s (ratio 0.81) |
| vio_B_v0.3_r1.png | S1 run 1: surge after a 10.7 s hold; agreement ~2% |
| vio_E_left_r1.png | S1 arc: phone yaw rate blind to the turn; 2.75 m VIO jump spike |
| phone_timing_debug_timeline.png | Debug run: depth→map time, tick rate, IMU age over 336 s |
| phone_timing_debug_vs_release.png | ECDFs of depth→map time and IMU age, Debug vs Release |
| phone_timing_ios_delivery.png | iOS IMU delivery CDF; 1.17 s stall at ARKit start |
| capture_tilt_side/top/persp.png | Capture 75eca1f97bcb: obstacle points on a tilted plane |
| capture_band_b0eca906.png | HorizonBand profile: band meets the floor at 2.84 m |
| route_narrow_path.png, route_narrow_path_cut.png | terra-mini route through a narrow gap, found vs cut |
| bucket_sim_examples.png | Zorvane frames: sunlit found, shaded and stand buckets missed |
| terraphone_architecture.png | TerraPhone Swift/Rust architecture |
| argos_light_*.png, zorvane_*.png | ARGOS light theme and Zorvane menus |
