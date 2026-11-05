# Attention metrics from ARGOS session logs

`attention_times.py` computes per-rover wait (WT), interaction (IT) and neglect (NT) time, checks, unprompted interventions, queueing wait (W_q) and operator blink rate from one ARGOS session log (`~/Documents/ARGOS Sessions/argos-session-*.jsonl`).

```sh
python3 attention_times.py "$HOME/Documents/ARGOS Sessions/argos-session-<id>.jsonl" --out results/
```

| Output | One row per |
| --- | --- |
| `*-episodes.csv` | help episode: onset, attend (touch), resume, WT, IT, NT before, W_q, how the operator first attended (select, video, gaze, command) |
| `*-checks.csv` | look at or selection of a working rover with no command within 5 s (paper: c, delta) |
| `*-unprompted.csv` | command to a working rover (paper: nu, IT^u) |
| `*-manual.csv` | L0/L1 span, with time spent driving |
| `*-summary.csv` | rover and level: means, medians, fan-out NT/(IT+WT)+1 |
| `*-operator.csv` | session: blink rate overall and while a rover waits, window time away, gaze share per rover |

Definitions (cycle per rover):

| Metric | From | To |
| --- | --- | --- |
| NT | rover resumes on its own | rover next needs help |
| WT | rover needs help | operator attends: select, video, gaze dwell >= 0.2 s, or first command |
| IT | operator attends | rover resumes |

Needs help = Terra `autonomy/status` at L2-L5 is done (`idle`, `task_idle`), blocked (any non-working reason) or stopped (emergency stop), for at least 1.5 s. Older logs without `rover_focus` or `gaze_dwell` fall back to the first command as the attend time, so their WT includes thinking time.

Logging and the webcam eye tracker are in ARGOS (`docs/src/pages/attention.md`, `scripts/argos_eye_tracker.py`).
