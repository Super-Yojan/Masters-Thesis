#!/usr/bin/env python3
"""Per-rover wait (WT), interaction (IT) and neglect (NT) time from an ARGOS session log.

Usage:  python3 attention_times.py SESSION.jsonl [--out DIR] [--debounce 1.5] [--gap 8]

Works on old logs (status + command records only). Newer ARGOS logs add
attention records, and the script uses them when present:
  rover_focus (select / video), gaze_dwell (eye tracker), help raised/cleared,
  blink, window_focus. Attend time t1 is then the first select, video or gaze
  dwell (>= --min-dwell s) on that rover, not the first command.

Cycle per rover (Olsen & Goodrich; Crandall & Cummings):
  NEGLECT --help onset--> WAIT --operator touches rover--> INTERACT --rover resumes--> NEGLECT
  WT = touch - onset     IT = resume - touch (or last command - touch)     NT = next onset - resume
"""
import argparse, csv, json, os, statistics as st
from collections import defaultdict

MANUAL = {"teleop", "assisted_teleop"}
# autonomy/status `reason` codes (Terra) -> what they mean for the operator.
DONE = {"idle", "task_idle"}                                   # finished, wants a new command
WORKING = {"active", "assisted", "driving_waypoint", "exploration_scan", "route_planning",
           "search_started", "search_unobserved_sector", "agent_driving", "awaiting_model",
           "awaiting_agent", "dock_lock", "dock_creep", "dock_settle", "dock_aligned",
           "dock_closing", "dock_dumping", "dock_backoff", "dock_reacquire"}
# everything else (route_no_path, obstacle_blocked, frontier_retry, map_stale, sensor_*,
# awaiting_operator, awaiting_drive_approval, heading_requires_spin_or_replan, ...) = BLOCKED
MIN_DWELL_S = 0.2       # a gaze dwell this long on a rover counts as attending to it
CHECK_WINDOW_S = 5.0    # a look not followed by a command within this is a check
COMMANDS = {"goal_sent", "goal_cancel_sent", "action_sent", "teleop_sent", "fleet_action"}


def load(path):
    with open(path, "rb") as f:
        for raw in f:
            if not raw.endswith(b"\n"):
                break  # interrupted final line
            try:
                yield json.loads(raw)
            except json.JSONDecodeError:
                continue


def classify(p, last_cmd_level):
    """One autonomy/status payload -> (state, level, why)."""
    level = p.get("requested_level") or p.get("effective_level") or last_cmd_level
    reason = p.get("reason") or ""
    if p.get("safety") == "emergency_stop":
        return "help", level, "stopped:" + reason
    if level in MANUAL:
        return "manual", level, reason
    if p.get("paused"):
        return "help", level, "paused"
    if reason in WORKING or (p.get("active_source") not in (None, "none") and reason not in DONE):
        return "work", level, reason
    if reason in DONE:
        return "help", level, "done:" + reason
    return "help", level, "blocked:" + reason


def debounce(samples, hold):
    """Keep a state change only if it lasts >= hold seconds (Terra flickers between
    hold reasons and active at ~10 Hz)."""
    out = []
    for t, s, lvl, why in samples:
        if out and out[-1][1] == s:
            continue
        out.append((t, s, lvl, why))
    keep = []
    for i, seg in enumerate(out):
        end = out[i + 1][0] if i + 1 < len(out) else float("inf")
        if end - seg[0] >= hold or not keep:
            if keep and keep[-1][1] == seg[1]:
                continue
            keep.append(seg)
    return keep


def analyse(path, debounce_s=1.5, gap_s=8.0):
    status = defaultdict(list)       # rover -> [(t, state, level, why)]
    touches = defaultdict(list)      # rover -> [(t, kind, detail)]
    focus = defaultdict(list)        # rover -> [(t, source)]  select / video / gaze
    blinks, window, offsets, dwells = [], [], [], []
    end_t, last_level = 0.0, {}
    for r in load(path):
        t, kind, rid = r.get("time"), r.get("kind"), r.get("rover_id")
        if isinstance(t, (int, float)):
            end_t = max(end_t, t)
            if isinstance(r.get("utc"), (int, float)) and len(offsets) < 2000:
                offsets.append(r["utc"] - t)
        if kind == "state_observed" and r.get("topic") == "autonomy/status" and isinstance(r.get("payload"), dict):
            status[rid].append((t,) + classify(r["payload"], last_level.get(rid)))
        elif kind in COMMANDS:
            for target in (r.get("targets") or [rid]):
                if target is None:
                    continue
                pay = r.get("payload") or {}
                if kind == "action_sent" and r.get("topic") == "autonomy" and isinstance(pay, dict) and pay.get("level"):
                    last_level[target] = pay["level"]
                if kind == "action_sent" and isinstance(pay, dict) and "assigned_level" in pay:
                    continue  # study-condition bookkeeping, not an operator act on the rover
                touches[target].append((t, kind, r.get("topic") or ""))
        elif kind == "rover_focus" and rid is not None:
            focus[rid].append((t, r.get("via", "select")))
        elif kind == "gaze_dwell":
            dwells.append(r)
        elif kind == "blink":
            blinks.append((t, r.get("duration_ms")))
        elif kind == "window_focus":
            window.append((t, bool(r.get("active"))))
    offset = st.median(offsets) if offsets else 0.0
    gaze_on = defaultdict(list)       # rover -> [(start, duration)] in session time
    for r in dwells:
        if r.get("rover_id") is None:
            continue
        start = (r["start_utc"] - offset) if isinstance(r.get("start_utc"), (int, float)) else r["time"] - r.get("duration_s", 0)
        gaze_on[r["rover_id"]].append((start, r.get("duration_s", 0.0)))
        if r.get("duration_s", 0.0) >= MIN_DWELL_S:
            focus[r["rover_id"]].append((start, "gaze"))
    episodes, unprompted, manual, checks = [], [], [], []
    for rid, samples in status.items():
        segs = debounce(sorted(samples, key=lambda x: x[0]), debounce_s)
        cmds = sorted(touches.get(rid, []))
        foc = sorted(focus.get(rid, []))
        resume_t = None
        for i, (t0, s, lvl, why) in enumerate(segs):
            t1 = segs[i + 1][0] if i + 1 < len(segs) else end_t
            if s == "manual":
                tele = [c[0] for c in cmds if t0 <= c[0] < t1 and c[1] == "teleop_sent"]
                busy, start, prev = 0.0, None, None
                for c in tele:
                    if start is None or c - prev > gap_s:
                        if start is not None:
                            busy += prev - start
                        start = c
                    prev = c
                if start is not None:
                    busy += prev - start
                manual.append(dict(rover=rid, level=lvl, start=t0, end=t1, span=t1 - t0, driving=busy))
                resume_t = None
                continue
            if s == "work":
                for c in cmds:
                    if t0 <= c[0] < t1 and c[1] != "teleop_sent":
                        unprompted.append(dict(rover=rid, level=lvl, time=c[0], command=c[1] + ":" + c[2]))
                # Checks: looked at or selected a working rover without commanding it.
                for ft, src in foc:
                    if t0 <= ft < t1 and not any(ft <= c[0] <= ft + CHECK_WINDOW_S for c in cmds):
                        look = sum(d for s0, d in gaze_on.get(rid, []) if abs(s0 - ft) < 1e-6)
                        checks.append(dict(rover=rid, level=lvl, time=ft, via=src, dwell_s=look or None))
                resume_t = t0
                continue
            # s == "help": one wait + interaction episode
            first_cmd = next((c for c in cmds if t0 <= c[0] <= t1 + 0.5), None)
            first = next(((f, src) for f, src in foc if t0 <= f <= t1), None)
            first_focus = first[0] if first else None
            touch = min(x for x in (first_focus, first_cmd and first_cmd[0], t1) if x is not None)
            burst = [c[0] for c in cmds if touch <= c[0] <= t1 + 0.5]
            last_cmd = burst[-1] if burst else None
            nxt = segs[i + 1][1] if i + 1 < len(segs) else None
            outcome = ("resumed" if nxt == "work" else "to_manual" if nxt == "manual"
                       else "session_end" if nxt is None else nxt)
            self_recovered = first_cmd is None and first_focus is None and nxt == "work"
            censored = first_cmd is None and first_focus is None and not self_recovered
            episodes.append(dict(
                rover=rid, level=lvl, cause=why, onset=t0, touch=touch, resume=t1, outcome=outcome,
                self_recovered=self_recovered, censored=censored, touch_source=first[1] if first and touch == first_focus else ("command" if first_cmd else "none"),
                commands=len(burst),
                WT=None if self_recovered or censored else touch - t0,
                IT=None if self_recovered or censored else t1 - touch,
                IT_cmd=None if not burst else last_cmd - touch,
                NT_before=None if resume_t is None else t0 - resume_t))
            resume_t = None
    # W_q: the part of each wait spent interacting with another rover.
    for e in episodes:
        if e["WT"] is None:
            continue
        busy = [(o["touch"], o["resume"]) for o in episodes
                if o is not e and o["rover"] != e["rover"] and o["IT"] is not None]
        e["Wq"] = overlap((e["onset"], e["touch"]), busy)
    operator = operator_summary(blinks, window, gaze_on, episodes, end_t)
    return episodes, unprompted, manual, checks, operator, end_t


def overlap(span, others):
    """Seconds of span covered by the union of others."""
    a, b = span
    cuts = sorted((max(a, x), min(b, y)) for x, y in others if y > a and x < b)
    total, edge = 0.0, a
    for x, y in cuts:
        x = max(x, edge)
        if y > x:
            total += y - x
            edge = y
    return total


def operator_summary(blinks, window, gaze_on, episodes, end_t):
    """Operator-level numbers: blink rate overall and while a rover waits, gaze share per rover."""
    if end_t <= 0:
        return {}
    waiting = [(e["onset"], e["touch"]) for e in episodes if e["WT"] is not None]
    wait_s = overlap((0, end_t), waiting)
    in_wait = sum(1 for t, _ in blinks if any(a <= t <= b for a, b in waiting))
    durations = [d for _, d in blinks if isinstance(d, (int, float))]
    away, last = 0.0, None
    for t, active in window:
        if last is not None and not last[1]:
            away += t - last[0]
        last = (t, active)
    if last is not None and not last[1]:
        away += end_t - last[0]
    row = dict(session_s=end_t, blinks=len(blinks),
               blink_rate_per_min=60 * len(blinks) / end_t if blinks else None,
               blink_rate_while_waiting=60 * in_wait / wait_s if blinks and wait_s > 0 else None,
               blink_rate_otherwise=60 * (len(blinks) - in_wait) / (end_t - wait_s) if blinks and end_t > wait_s else None,
               blink_duration_ms_median=st.median(durations) if durations else None,
               window_away_s=away if window else None)
    for rover, spans in sorted(gaze_on.items()):
        row[f"gaze_share_rover_{rover}"] = sum(d for _, d in spans) / end_t
    return row


def mean(xs):
    xs = [x for x in xs if x is not None]
    return (st.mean(xs), st.median(xs), len(xs)) if xs else (None, None, 0)


def summarise(episodes, unprompted, manual, checks, end_t):
    rows = []
    keys = sorted({(e["rover"], e["level"]) for e in episodes} | {(m["rover"], m["level"]) for m in manual},
                  key=lambda k: (str(k[0]), str(k[1])))
    for rover, level in keys:
        ep = [e for e in episodes if e["rover"] == rover and e["level"] == level]
        mn = [m for m in manual if m["rover"] == rover and m["level"] == level]
        wt, it, nt = (mean([e[k] for e in ep]) for k in ("WT", "IT", "NT_before"))
        if mn:  # manual control: the operator is the controller, NT = 0
            it = mean([m["driving"] for m in mn]); nt = (0.0, 0.0, len(mn)); wt = (0.0, 0.0, len(mn))
        fo = None
        if nt[0] is not None and it[0] and (it[0] + (wt[0] or 0)) > 0:
            fo = nt[0] / (it[0] + (wt[0] or 0)) + 1
        rows.append(dict(rover=rover, level=level, episodes=len(ep) or len(mn),
                         self_recovered=sum(e["self_recovered"] for e in ep),
                         WT_mean=wt[0], WT_median=wt[1], IT_mean=it[0], IT_median=it[1],
                         NT_mean=nt[0], NT_median=nt[1],
                         Wq_mean=mean([e.get("Wq") for e in ep])[0],
                         unprompted=sum(1 for u in unprompted if u["rover"] == rover and u["level"] == level),
                         checks=sum(1 for c in checks if c["rover"] == rover and c["level"] == level),
                         fan_out=fo))
    return rows


def write(rows, path):
    if not rows:
        return
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("log")
    ap.add_argument("--out", default=".")
    ap.add_argument("--debounce", type=float, default=1.5, help="min seconds a state must last")
    ap.add_argument("--gap", type=float, default=8.0, help="teleop gap that ends a driving burst")
    ap.add_argument("--min-dwell", type=float, default=0.2, help="gaze dwell (s) that counts as attending")
    a = ap.parse_args()
    MIN_DWELL_S = a.min_dwell
    eps, unp, man, chk, operator, end_t = analyse(a.log, a.debounce, a.gap)
    rows = summarise(eps, unp, man, chk, end_t)
    os.makedirs(a.out, exist_ok=True)
    base = os.path.join(a.out, os.path.basename(a.log).rsplit(".", 1)[0])
    write(eps, base + "-episodes.csv"); write(unp, base + "-unprompted.csv")
    write(man, base + "-manual.csv"); write(rows, base + "-summary.csv")
    write(chk, base + "-checks.csv"); write([operator] if operator else [], base + "-operator.csv")
    fmt = lambda v: "-" if v is None else f"{v:.1f}"
    print(f"{'rover':>5} {'level':>16} {'n':>3} {'self':>4} {'WT':>6} {'IT':>6} {'NT':>6} {'unpr':>4} {'FO':>5}")
    for r in rows:
        print(f"{str(r['rover']):>5} {str(r['level']):>16} {r['episodes']:>3} {r['self_recovered']:>4} "
              f"{fmt(r['WT_mean']):>6} {fmt(r['IT_mean']):>6} {fmt(r['NT_mean']):>6} {r['unprompted']:>4} {fmt(r['fan_out']):>5}")
    if operator.get("blinks"):
        print(f"blinks {operator['blinks']} · {fmt(operator['blink_rate_per_min'])}/min overall · "
              f"{fmt(operator['blink_rate_while_waiting'])}/min while a rover waits")
    print(f"session {end_t:.0f} s · episodes, checks, unprompted, manual, operator and summary CSVs in {a.out}")
