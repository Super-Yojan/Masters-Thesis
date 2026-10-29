"""Stability analysis of Terra's control loops: plant fit, margins, nonlinear effects, L3.

Run from this folder:  python3 analysis.py
Writes thesis/figures/ctl_*.pdf and results.json. Needs numpy, matplotlib.
Data: data/*.csv, extracted from the phone journal of 2026-10-26 (events.db, about 8-10 Hz).
"""
import itertools
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from terra_loop import PI, Turning, margins, loop, run, simulate, wrap

HERE = Path(__file__).parent
FIG = HERE.parent.parent / "thesis" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
C1, C2, C3, C4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"  # categorical order
INK, MUTED = "#222222", "#8a8a8a"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": "#e6e6e6", "grid.linewidth": 0.6,
                     "lines.linewidth": 1.6, "legend.frameon": False, "figure.dpi": 150})
R = {}
SCALE = 0.88          # phone / OptiTrack distance ratio, sessions 2 and 4
W = np.logspace(-3, 2.5, 40000)

# ------------------------------------------------------------------ 1. plant fit
steps = []
for b, dur in (("12", 13.2896), ("14", 12.2653)):
    s = np.loadtxt(HERE / f"data/step_boot{b}_speed.csv", delimiter=",", skiprows=1)
    e = np.loadtxt(HERE / f"data/step_boot{b}_effort.csv", delimiter=",", skiprows=1)
    steps.append((s, e, dur))


def fit_cost(Kp, d, tau, L):
    err = 0
    for s, _, dur in steps:
        ref = lambda x, dur=dur: 0.3 if 0.5 <= x < 0.5 + dur else 0.0
        t, v, me, u = simulate(ref, K=Kp / SCALE, d=d, tau=tau, L=L, T=s[-1, 0] + 0.05)
        err += np.mean((np.interp(s[:, 0], t, me) - s[:, 1]) ** 2)
    return np.sqrt(err / len(steps))


grid = [(fit_cost(*p), *p) for p in itertools.product(
    np.arange(0.85, 1.051, 0.02), [0.0, 0.03, 0.05, 0.06, 0.07, 0.09],
    [0.02, 0.05, 0.08, 0.12, 0.2], [0.05, 0.1, 0.15, 0.2, 0.25, 0.3])]
grid.sort()
best = grid[0]
near = [g for g in grid if g[0] <= best[0] * 1.02]
KP, DB, TAU, LP = best[1:]
R["plant_fit"] = {"rms_mps": best[0], "K_phone": KP, "K_true": KP / SCALE, "deadband": DB, "tau_s": TAU,
                  "delay_s": LP, "K_phone_range_within_2pct": [min(g[1] for g in near), max(g[1] for g in near)],
                  "deadband_range": [min(g[2] for g in near), max(g[2] for g in near)],
                  "delay_range": [min(g[4] for g in near), max(g[4] for g in near)],
                  "tau_range": [min(g[3] for g in near), max(g[3] for g in near)]}
KT = KP / SCALE
# Effort needed to hold 0.3 m/s (phone) in steady state, measured.
R["steady_effort_at_0p3"] = [float(np.median(e[(e[:, 0] > 5) & (e[:, 0] < 0.5 + dur), 1])) for _, e, dur in steps]

fig, ax = plt.subplots(2, 1, figsize=(6.2, 4.4), sharex=True)
for i, (s, e, dur) in enumerate(steps):
    lbl = "measured (phone VIO)" if i == 0 else None
    ax[0].plot(s[:, 0] - 0.5, s[:, 1], "o", ms=2.5, color=MUTED, label=lbl)
    ax[1].plot(e[:, 0] - 0.5, e[:, 1], "o", ms=2.5, color=MUTED, label="measured" if i == 0 else None)
ref = lambda x: 0.3 if 0.5 <= x < 0.5 + 13.29 else 0.0
t, v, me, u = simulate(ref, K=KT, d=DB, tau=TAU, L=LP, T=16.5)
ax[0].plot(t - 0.5, me, color=C1, label="model, phone frame")
ax[0].plot(t - 0.5, v, color=C2, lw=1.2, ls="--", label="model, true speed")
ax[0].axhline(0.3, color=INK, lw=0.8, ls=":")
ax[1].plot(t - 0.5, u, color=C1, label="model")
ax[1].plot(t - 0.5, np.where((t >= 0.5) & (t < 13.79), 0.1, 0), color=C3, lw=1.2, ls="--", label="feedforward part")
ax[0].set_ylabel("forward speed (m/s)")
ax[1].set_ylabel("mean wheel effort")
ax[1].set_xlabel("time since 0.3 m/s step (s)")
ax[0].legend(loc="lower right", fontsize=8)
ax[1].legend(loc="lower right", fontsize=8)
fig.tight_layout()
fig.savefig(FIG / "ctl_step_fit.pdf")
plt.close(fig)

# rise time of the as-built loop and of a loop with matched feedforward
def rise(ff, kp=0.3, ki=0.6, r0=0.3):
    t, v, me, u = simulate(lambda x: r0, K=KT, d=DB, tau=TAU, L=LP, ctl=PI(kp=kp, ki=ki, ff=ff), T=15)
    return float(t[np.flatnonzero(me >= 0.9 * r0)[0]])


R["rise90_s"] = {"as_built": rise(1 / 3), "ff_matched": rise(1 / KP)}
R["startup"] = {}
for r0 in (0.05, 0.1, 0.2, 0.3):
    t, v, me, u = simulate(lambda x, r0=r0: r0, K=KT, d=DB, tau=TAU, L=LP, T=12)
    R["startup"][r0] = {"first_motion_s": float(t[np.flatnonzero(v > 0.01)[0]]),
                        "rise90_s": float(t[np.flatnonzero(me >= 0.9 * r0)[0]])}

# ------------------------------------------------------------------ 2. linear margins
VIO_LAG, TF = 0.06, 0.03


def theta(tick=0.01, every=5):
    """Lumped loop delay: plant + VIO lag + half the motor-write hold + half a tick."""
    return LP + VIO_LAG + every * tick / 2 + tick / 2


CASES = [
    ("As built, Release (100 Hz)", 0.3, 0.6, KP, theta()),
    ("As built, Debug (17 Hz)", 0.3, 0.6, KP, theta(1 / 17)),
    ("As built, VIO scale 0.60", 0.3, 0.6, KP / SCALE * 0.60, theta()),
    ("As built, VIO scale 1.00", 0.3, 0.6, KP / SCALE, theta()),
    ("Design assumption, $K$ = 3 m/s", 0.3, 0.6, 3.0, theta()),
    ("Profile rule with top\\_speed 1.0", 0.9, 1.8, KP, theta()),
    ("Profile rule, Debug (17 Hz)", 0.9, 1.8, KP, theta(1 / 17)),
    ("Matched feedforward, kp 0.3, ki 0.6", 0.3, 0.6, KP, theta()),
]
R["margins"] = []
for name, kp, ki, K, th in CASES:
    m = margins(loop(W, kp, ki, K, TAU, th, TF), W)
    R["margins"].append({"case": name, "kp": kp, "ki": ki, "K_loop": K, "delay_ms": th * 1e3,
                         "wc": m["wc"], "fc_hz": m["wc"] / 2 / np.pi, "pm_deg": m["pm"], "dm_ms": m["dm"] * 1e3,
                         "w180": m["w180"], "f180_hz": m["w180"] / 2 / np.pi, "gm_db": m["gm_db"],
                         "kpK": kp * K})
# the older rough budget: (100 - 45) deg at 0.4 Hz
R["old_budget_ms"] = (100 - 45) / (360 * 0.4) * 1e3

fig, ax = plt.subplots(2, 1, figsize=(6.2, 4.6), sharex=True)
for (name, kp, ki, K, th), col in zip([CASES[0], CASES[4], CASES[5], CASES[1]], (C1, C2, C3, C4)):
    Lf = loop(W, kp, ki, K, TAU, th, TF)
    m = margins(Lf, W)
    ls = (0, (4, 3)) if "Debug" in name else "-"
    ax[0].semilogx(W / 2 / np.pi, 20 * np.log10(np.abs(Lf)), color=col, ls=ls, label=name.replace("\\_", "_"))
    ax[1].semilogx(W / 2 / np.pi, np.degrees(np.unwrap(np.angle(Lf))), color=col, ls=ls)
    ax[0].plot(m["wc"] / 2 / np.pi, 0, "o", color=col, ms=4)
for a in ax:
    a.set_xlim(1e-2, 10)
ax[0].axhline(0, color=INK, lw=0.8)
ax[0].set_ylim(-30, 40)
ax[1].axhline(-180, color=INK, lw=0.8)
ax[1].set_ylim(-540, -60)
ax[0].set_ylabel("$|L(j\\omega)|$ (dB)")
ax[1].set_ylabel("phase (deg)")
ax[1].set_xlabel("frequency (Hz)")
ax[0].legend(fontsize=7.5, loc="upper right")
fig.tight_layout()
fig.savefig(FIG / "ctl_bode.pdf")
plt.close(fig)

# delay budget (Release vs Debug) against the delay margins
comp = [("Motor, ESC and link (fit)", LP, LP), ("VIO behind gyro", VIO_LAG, VIO_LAG),
        ("Motor write hold (5 ticks / 2)", 0.025, 5 / 17 / 2), ("Tick (1/2)", 0.005, 1 / 17 / 2)]
R["delay_budget_ms"] = {"release": sum(c[1] for c in comp) * 1e3, "debug": sum(c[2] for c in comp) * 1e3,
                        "components": {c[0]: [c[1] * 1e3, c[2] * 1e3] for c in comp}}
fig, ax = plt.subplots(figsize=(6.2, 3.0))
for row, idx, lab in ((1, 1, "Release, 100 Hz tick"), (0, 2, "Debug, 17 Hz tick")):
    left = 0
    for c, col in zip(comp, (C1, C2, C3, C4)):
        ax.barh(row, c[idx] * 1e3, left=left, color=col, height=0.55, edgecolor="white", linewidth=2,
                label=c[0] if row == 1 else None)
        left += c[idx] * 1e3
    ax.text(left + 8, row, f"{left:.0f} ms", va="center", fontsize=8, color=INK)
dm_as = R["margins"][0]["dm_ms"]
dm_rule = R["margins"][5]["dm_ms"]
dm_des = R["margins"][4]["dm_ms"]
for x, txt, yy in ((dm_des, f"delay margin, design $K$=3: {dm_des:.0f} ms", 1.55),
                  (dm_rule, f"delay margin, profile rule: {dm_rule:.0f} ms", 1.9)):
    ax.axvline(x, color=INK, lw=0.9, ls=":")
    ax.text(x + 6, yy, txt, fontsize=7.5, color=INK)
ax.text(715, 0.5, f"as built: {dm_as / 1e3:.1f} s, off scale", fontsize=7.5, color=MUTED, ha="right")
ax.set_yticks([0, 1], ["Debug, 17 Hz tick", "Release, 100 Hz tick"])
ax.set_xlim(0, 720)
ax.set_ylim(-0.5, 2.15)
ax.set_xlabel("loop delay (ms)")
ax.grid(axis="y", visible=False)
ax.legend(fontsize=7, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.32))
fig.tight_layout()
fig.savefig(FIG / "ctl_delay_budget.pdf")
plt.close(fig)

# ------------------------------------------------------------------ 3. holds and windup
gh = np.loadtxt(HERE / "data/gate_hold_boot12.csv", delimiter=",", skiprows=1)
c = PI()
model_ramp = []
for k in range(int(14 / 0.01)):
    tt = k * 0.01
    model_ramp.append((tt, c.step(0.3, 0.0) if tt < 13.29 else c.step(0.0, 0.0)))
model_ramp = np.array(model_ramp)
R["gate_hold_integral"] = float(PI().I)
c = PI()
for _ in range(1000):
    c.step(0.3, 0.0)
R["gate_hold_integral"] = float(c.I)
R["gate_hold_ramp_rate"] = 0.6 * 0.3

ref = lambda x: 0.3 if x >= 1 else 0.0
runs = {}
for key, kw in (("gate", dict(gate_hold=lambda x: x < 11)), ("reset", dict(ctl_hold=lambda x: x < 11)),
                ("freeze", None)):
    if kw is None:
        continue
    runs[key] = simulate(ref, K=KT, d=DB, tau=TAU, L=LP, T=22, **kw)
t, v, me, u = runs["gate"]
m = t > 11
R["gate_release"] = {"peak_true_mps": float(v[m].max()), "peak_after_s": float(t[m][np.argmax(v[m])] - 11),
                     "target_true_mps": 0.3 / SCALE}
R["periodic_reset"] = {}
for per, dur in ((2.0, 0.15), (1.05, 0.15), (0.5, 0.15)):
    t2, v2, me2, u2 = simulate(lambda x: 0.3, K=KT, d=DB, tau=TAU, L=LP, T=40,
                               ctl_hold=lambda x, per=per, dur=dur: (x % per) < dur and x > 2)
    R["periodic_reset"][per] = float(v2[t2 > 20].mean())
R["periodic_reset"]["none"] = 0.3 / SCALE
per_trace = simulate(lambda x: 0.3, K=KT, d=DB, tau=TAU, L=LP, T=12,
                     ctl_hold=lambda x: (x % 1.05) < 0.15 and x > 4)

fig, ax = plt.subplots(1, 3, figsize=(6.6, 2.5))
ax[0].plot(gh[:, 0], gh[:, 2], "o", ms=2.5, color=MUTED, label="measured")
ax[0].plot(model_ramp[:, 0], model_ramp[:, 1], color=C1, lw=1.0, ls="--", label="model")
ax[0].set_title("(a) effort under a gate hold", fontsize=8.5)
ax[0].set_xlabel("time (s)")
ax[0].set_ylabel("mean wheel effort")
ax[0].legend(fontsize=7, loc="lower right")
ax[0].set_xlim(-1, 16)
for key, col, lab in (("gate", C2, "gate hold (integrator runs)"), ("reset", C1, "controller hold (reset)")):
    t, v, me, u = runs[key]
    ax[1].plot(t - 11, v, color=col, label=lab)
ax[1].axhline(0.3 / SCALE, color=INK, lw=0.8, ls=":")
ax[1].set_xlim(-1, 10)
ax[1].set_title("(b) release after a 10 s hold", fontsize=8.5)
ax[1].set_xlabel("time since release (s)")
ax[1].set_ylabel("true speed (m/s)")
ax[1].legend(fontsize=6.5, loc="upper right")
t, v, me, u = per_trace
ax[2].plot(t, v, color=C1)
ax[2].axhline(0.3 / SCALE, color=INK, lw=0.8, ls=":")
ax[2].set_title("(c) 150 ms resets every 1.05 s", fontsize=8.5)
ax[2].set_xlabel("time (s)")
ax[2].set_ylabel("true speed (m/s)")
fig.tight_layout()
fig.savefig(FIG / "ctl_holds.pdf")
plt.close(fig)

# ------------------------------------------------------------------ 4. deadband describing function (terra-mini)
TS, DC = 0.8, 0.3
mini = dict(kp=0.9 / TS, ki=1.8 / TS, ff=1 / TS)
R["mini"] = []
fig, ax = plt.subplots(1, 2, figsize=(6.6, 3.3))
for dt_true, col in ((0.3, C1), (0.2, C2), (0.1, C3)):
    Km = TS / (1 - dt_true)
    Kin = Km * (1 - DC) * SCALE
    Lf = loop(W, mini["kp"], mini["ki"], Kin, TAU, theta(), TF)
    mm = margins(Lf, W)
    gm = 10 ** (mm["gm_db"] / 20)
    h = (DC - dt_true) / (1 - DC)
    A = 4 * h / (np.pi * (gm - 1)) if h > 0 else 0.0
    t, v, me, u = simulate(lambda x: 0.1, K=Km, d=dt_true, tau=TAU, L=LP, ctl=PI(deadband=DC, **mini), T=30)
    sel = t > 15
    x = me[sel] - me[sel].mean()
    f = np.fft.rfftfreq(len(x), 0.01)
    fsim = float(f[np.argmax(np.abs(np.fft.rfft(x)))]) if np.ptp(me[sel]) > 1e-3 else None
    R["mini"].append({"true_deadband": dt_true, "gm_db": mm["gm_db"], "f180_hz": mm["w180"] / 2 / np.pi,
                      "relay_h": h, "pred_amplitude_effort": A, "sim_speed_pp": float(np.ptp(me[sel])),
                      "sim_freq_hz": fsim, "wc": mm["wc"], "pm": mm["pm"]})
    sel_w = (W > 0.3) & (W < 60)
    ax[0].plot(Lf[sel_w].real, Lf[sel_w].imag, color=col, lw=1.2, label=f"true deadband {dt_true}")
    ax[1].plot(t[(t > 20) & (t < 24)] - 20, v[(t > 20) & (t < 24)], color=col, label=f"true deadband {dt_true}")
amp = np.logspace(-3, 1, 400)
N = 1 + 4 * ((DC - 0.1) / (1 - DC)) / (np.pi * amp)
ax[0].plot(-1 / N, 0 * N, color=INK, lw=3, alpha=0.35, label="$-1/N(A)$, relay part")
ax[0].plot(-1, 0, "x", color=INK)
ax[0].set_xlim(-1.4, 0.4)
ax[0].set_ylim(-1.0, 0.6)
ax[0].set_title("(a) Nyquist, terra-mini speed loop", fontsize=8.5)
ax[0].legend(fontsize=6.5, loc="upper left", bbox_to_anchor=(0.0, -0.25), ncol=2)
ax[0].set_xlabel("Re $L$")
ax[0].set_ylabel("Im $L$")
ax[1].axhline(0.1 / SCALE, color=INK, lw=0.8, ls=":")
ax[1].set_title("(b) simulated, target 0.1 m/s", fontsize=8.5)
ax[1].set_xlabel("time (s)")
ax[1].set_ylabel("true speed (m/s)")
fig.tight_layout()
fig.savefig(FIG / "ctl_deadband_df.pdf")
plt.close(fig)

# ------------------------------------------------------------------ 5. yaw and heading (L3) loops
s_ = 1j * W
th_yaw = LP + 0.025 + 0.005  # gyro has no VIO lag
R["yaw"] = []
for Kpsi in (1.6, 5.0):
    P = Kpsi * np.exp(-th_yaw * s_) / (TAU * s_ + 1)
    C = 0.1 + 0.3 / s_
    my = margins(C * P, W)
    T = P * (0.2 + C) / (1 + P * C)
    mh = margins(1.6 * T / s_, W)
    R["yaw"].append({"K_psi": Kpsi, "yaw_wc": my["wc"], "yaw_pm": my["pm"], "yaw_gm_db": my["gm_db"],
                     "yaw_dm_ms": my["dm"] * 1e3, "head_wc": mh["wc"], "head_pm": mh["pm"],
                     "head_gm_db": mh["gm_db"], "head_dm_ms": mh["dm"] * 1e3})

goal = (30 * np.cos(0.5), 30 * np.sin(0.5))
R["l3_heading"] = []
fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.7))
for (Kpsi, cruise, lim), col, ls in (((1.6, 0.3, True), C1, "-"), ((1.6, 1.0, True), C2, "-"),
                                     ((5.0, 1.0, True), C3, "-"), ((1.6, 1.0, False), C2, "--")):
    tl = Turning() if lim else Turning(maxw=5, acc=100, dec=100, R=1e-6, inplace=True)
    o = run([goal], cruise=cruise, Kpsi=Kpsi, T=20, turning=tl, Kv=KT, d=DB, L=LP, tau=TAU)
    e = wrap(np.arctan2(goal[1] - o[:, 2], goal[0] - o[:, 1]) - o[:, 3])
    i = np.flatnonzero(np.abs(e) > np.radians(3))
    R["l3_heading"].append({"K_psi": Kpsi, "cruise": cruise, "limiter": lim,
                            "overshoot_deg": float(np.degrees(max(-e.min(), 0))),
                            "settle_3deg_s": float(o[i[-1], 0]) if len(i) else 0.0,
                            "peak_yaw_rate": float(o[:, 5].max())})
    lab = f"$K_\\psi$ {Kpsi}, cruise {cruise}" + ("" if lim else ", no limiter")
    ax[0].plot(o[:, 0], np.degrees(e), color=col, ls=ls, label=lab)
ax[0].axhline(0, color=INK, lw=0.8)
ax[0].set_xlabel("time (s)")
ax[0].set_ylabel("bearing error (deg)")
ax[0].set_title("(a) 0.5 rad bearing step", fontsize=8.5)
ax[0].legend(fontsize=6.5)
D = np.linspace(0.2, 5, 200)
for v_, col in ((0.3, C1), (0.6, C4), (1.0, C2)):
    ax[1].plot(D, 0.5 * np.sqrt(1.6 * D / v_), color=col, label=f"$v$ = {v_} m/s")
ax[1].axhline(0.7, color=INK, lw=0.8, ls=":")
ax[1].axhline(1.0, color=MUTED, lw=0.8, ls=":")
ax[1].set_xlabel("distance to pursued point $D$ (m)")
ax[1].set_ylabel("damping ratio $\\zeta$")
ax[1].set_title("(b) cross-track damping", fontsize=8.5)
ax[1].legend(fontsize=6.5, loc="lower right")
fig.tight_layout()
fig.savefig(FIG / "ctl_l3.pdf")
plt.close(fig)


def clean(x):
    if isinstance(x, dict):
        return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else round(float(x), 4)
    if isinstance(x, np.integer):
        return int(x)
    return x


(HERE / "results.json").write_text(json.dumps(clean(R), indent=1))
print(json.dumps(clean(R), indent=1))
