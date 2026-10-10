# Graph Report - .  (2026-10-05)

## Corpus Check
- Corpus is ~7,209 words - fits in a single context window. You may not need a graph.

## Summary
- 97 nodes · 110 edges · 15 communities (9 shown, 6 thin omitted)
- Extraction: 97% EXTRACTED · 1% INFERRED · 2% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Thesis Papers and Metrics|Thesis Papers and Metrics]]
- [[_COMMUNITY_Terra Robotics Architecture|Terra Robotics Architecture]]
- [[_COMMUNITY_Phone-Only Navigation Feasibility|Phone-Only Navigation Feasibility]]
- [[_COMMUNITY_ARGOS Fleet Supervision|ARGOS Fleet Supervision]]
- [[_COMMUNITY_Human Workload Experiments|Human Workload Experiments]]
- [[_COMMUNITY_Depth Sensing and Simulation|Depth Sensing and Simulation]]
- [[_COMMUNITY_Obstacle Mapping Pipeline|Obstacle Mapping Pipeline]]
- [[_COMMUNITY_Phone Integration and UniFFI|Phone Integration and UniFFI]]
- [[_COMMUNITY_Attention and Urgency|Attention and Urgency]]
- [[_COMMUNITY_Future Mission Autonomy|Future Mission Autonomy]]
- [[_COMMUNITY_Future Fleet Autonomy|Future Fleet Autonomy]]
- [[_COMMUNITY_Waypoint Navigation|Waypoint Navigation]]
- [[_COMMUNITY_Coordinate Frame Transforms|Coordinate Frame Transforms]]
- [[_COMMUNITY_Evaluation Script Placeholder|Evaluation Script Placeholder]]
- [[_COMMUNITY_Paper Draft Collection|Paper Draft Collection]]

## God Nodes (most connected - your core abstractions)
1. `Terra` - 25 edges
2. `ARGOS` - 14 edges
3. `Fleet size × autonomy level study` - 11 edges
4. `Phone-as-brain fleet thesis outline` - 10 edges
5. `ARGOS joining brief` - 8 edges
6. `Phone-only waypoint navigation decision problem` - 7 edges
7. `Paper 2 collaborative SLAM and shared maps` - 6 edges
8. `Paper 3 dashboard and attention scheduling` - 6 edges
9. `Phone-as-brain rover feasibility introduction` - 6 edges
10. `DWA Dynamic Window Approach` - 5 edges

## Surprising Connections (you probably didn't know these)
- `Chen 2018 AR/VR survey citation (placeholder)` --conceptually_related_to--> `ARGOS`  [AMBIGUOUS]
  thesis/thesis_outline.pdf → docs/ARGOS_CURRENT_SUMMARY.md
- `Phone-as-brain fleet thesis outline` --references--> `ARGOS`  [EXTRACTED]
  thesis/thesis_outline.pdf → docs/ARGOS_CURRENT_SUMMARY.md
- `Phone-as-brain fleet thesis outline` --references--> `Terra`  [EXTRACTED]
  thesis/thesis_outline.pdf → docs/ARGOS_CURRENT_SUMMARY.md
- `Phone-as-brain fleet thesis outline` --references--> `Urgency classifier`  [EXTRACTED]
  thesis/thesis_outline.pdf → docs/ARGOS_CURRENT_SUMMARY.md
- `Phone-as-brain fleet thesis outline` --references--> `NASA-TLX`  [EXTRACTED]
  thesis/thesis_outline.pdf → docs/ARGOS_CURRENT_SUMMARY.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Three-paper shared-platform research spine** — thesis_papers_research_questions_paper_1_phone_as_brain_feasibility, thesis_papers_research_questions_paper_2_collaborative_slam_and_shared_maps, thesis_papers_research_questions_paper_3_dashboard_and_attention_scheduling [EXTRACTED 1.00]
- **Robot attention to operator scheduling** — docs_argos_current_summary_terra, docs_argos_current_summary_attention_signals, docs_argos_current_summary_urgency_classifier, docs_argos_current_summary_argos, docs_argos_current_summary_argos_station [EXTRACTED 1.00]

## Communities (15 total, 6 thin omitted)

### Community 0 - "Thesis Papers and Metrics"
Cohesion: 0.12
Nodes (19): ARGOS dashboard and attention scheduling, Collaborative mapping, Phone-as-brain feasibility, Phone-as-brain feasibility draft, Collaborative SLAM paper (placeholder), ARGOS dashboard paper (placeholder), Three-paper thesis spine, Absolute and relative localization error (+11 more)

### Community 1 - "Terra Robotics Architecture"
Cohesion: 0.12
Nodes (17): Body coordinate frame, Experimental event logging, Rust robotics libraries, Terra, terra-control, terra-mapping, terra-mobile, terra-nav (intended) (+9 more)

### Community 2 - "Phone-Only Navigation Feasibility"
Cohesion: 0.14
Nodes (15): DWA Dynamic Window Approach, L3 Local autonomy, Wheel-velocity control, Consumer phone as sole onboard brain, Dedicated-compute baseline, Disaster recovery fleet, Fox Burgard Thrun 1997 Dynamic Window Approach, Phone-as-brain rover feasibility introduction (+7 more)

### Community 3 - "ARGOS Fleet Supervision"
Cohesion: 0.17
Nodes (13): ARGOS, Bevy/Avian simulator, Capability matching (future), cmd_vel debug path, Go-to-waypoint contract, High-bandwidth detail on demand, Low-bandwidth continuous awareness, Operator LLM (+5 more)

### Community 4 - "Human Workload Experiments"
Cohesion: 0.18
Nodes (12): Attention response time, Fleet size × autonomy level study, Human interventions, L0 Teleoperation, L1 Waypoint following, L2 Stop and ask, NASA-TLX, Chen 2018 AR/VR survey citation (placeholder) (+4 more)

### Community 5 - "Depth Sensing and Simulation"
Cohesion: 0.50
Nodes (4): iPhone LiDAR, Monocular depth, Simulator ground truth, Unreal visual simulation

### Community 6 - "Obstacle Mapping Pipeline"
Cohesion: 0.50
Nodes (4): Depth frame, Obstacle inflation, Occupancy grid, DepthFrame

### Community 7 - "Phone Integration and UniFFI"
Cohesion: 0.50
Nodes (4): Bluetooth chassis link, TerraPhone, UniFFI, UniFFI not-yet-in-repository claim

### Community 8 - "Attention and Urgency"
Cohesion: 0.67
Nodes (3): argos-station, Attention signals, Urgency classifier

## Ambiguous Edges - Review These
- `ARGOS` → `Chen 2018 AR/VR survey citation (placeholder)`  [AMBIGUOUS]
  thesis/thesis_outline.pdf · relation: conceptually_related_to
- `UniFFI` → `UniFFI not-yet-in-repository claim`  [AMBIGUOUS]
  presentation/argos-onboarding-deck.html · relation: conceptually_related_to

## Knowledge Gaps
- **60 isolated node(s):** `TerraPhone VLA`, `Operator LLM`, `Low-bandwidth continuous awareness`, `High-bandwidth detail on demand`, `Human interventions` (+55 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `ARGOS` and `Chen 2018 AR/VR survey citation (placeholder)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `UniFFI` and `UniFFI not-yet-in-repository claim`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Terra` connect `Terra Robotics Architecture` to `Thesis Papers and Metrics`, `Phone-Only Navigation Feasibility`, `ARGOS Fleet Supervision`, `Human Workload Experiments`, `Attention and Urgency`?**
  _High betweenness centrality (0.332) - this node is a cross-community bridge._
- **Why does `ARGOS` connect `ARGOS Fleet Supervision` to `Attention and Urgency`, `Terra Robotics Architecture`, `Human Workload Experiments`, `Thesis Papers and Metrics`?**
  _High betweenness centrality (0.206) - this node is a cross-community bridge._
- **Why does `Fleet size × autonomy level study` connect `Human Workload Experiments` to `Thesis Papers and Metrics`, `Phone-Only Navigation Feasibility`, `ARGOS Fleet Supervision`?**
  _High betweenness centrality (0.188) - this node is a cross-community bridge._
- **What connects `TerraPhone VLA`, `Operator LLM`, `Low-bandwidth continuous awareness` to the rest of the system?**
  _60 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Thesis Papers and Metrics` be split into smaller, more focused modules?**
  _Cohesion score 0.11695906432748537 - nodes in this community are weakly interconnected._
## Token Accounting Limitation

The extraction agent API did not expose usage counts. Zero values above are placeholders, not a measured zero-token cost.
