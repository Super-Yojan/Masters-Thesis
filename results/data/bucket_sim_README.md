# YOLO bucket model on Zorvane (2026-10-27)

Model: Terra `models/yolo26n-rover/weights/best.pt` (same weights as the Core ML package), run with Ultralytics at 640 px, conf 0.25.
Scene: Zorvane NEXT field, 4 parked rovers on the goal lines (2 face north, 2 south), 9 bucket seeds chosen so buckets land 2–12 m ahead.
Ground truth: bucket/ball layout recomputed from the seed, projected through the depth packet's camera pose, occlusion checked with depth.
Rovers were not driven: on the cloud's software GPU the sim's obstacle map goes stale, so goals and teleop hold.

| Run | Blue, ground | Blue, 1 m stand | Orange, ground | Orange, stand | False buckets | Colour right |
| --- | --- | --- | --- | --- | --- | --- |
| Noon, sim camera 256×192 | 21/22 | 0/4 | 4/18 | 0/6 | 0 | 25/25 |
| Noon, 1024×768 (local patch) | 21/22 | 1/4 | 5/18 | 0/6 | 0 | 27/27 |
| Overcast, 1024×768 | 8/18 | 1/3 | 14/14 | 1/4 | 2 | 25/25 |

Buckets within 10 m. Beyond 10 m: 1 of 126 found.

- Blue buckets were always seen by the south rovers and orange by the north ones, so colour and sun side are mixed. At noon the north rovers see the shaded side (orange renders as RGB ~92,42,25) and miss it; overcast flips which side is found. The model struggles with dark, shaded buckets.
- Buckets on 1 m stands are mostly missed (3/17).
- Confidence of found buckets: median about 0.75, many below 0.8, so Terra's 0.8 search confirmation would reject many sightings.
- Balls (≥8 px, high-res): 27/185 at noon, 103/124 overcast.

Files: `examples.png`, `eval_*.json` (per-frame boxes), `scripts/` (capture, scoring, layout generator).
