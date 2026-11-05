"""Figures for the VIO-vs-OptiTrack section of the conference draft.

Ratios are copied from thesis Table tab:vio-scale (ch5_autonomy.tex), which
comes from the Oct 26-27, 2026 motion-capture sessions. The example trace is
cropped from the session-1 analysis plot B_v0.3_r2.png
(/mnt/project-files/velocity-experiment/session-2026-10-26/).
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

RATIOS = {
    "S1 (Oct 26)": [0.98, 0.81],
    "S2 (Oct 26)": [0.81, 0.89, 0.93, 0.88],
    "S3 (Oct 26)": [1.01],
    "S4 (Oct 27)": [0.83, 0.60, 0.93, 0.95, 0.92, 0.86, 0.90, 1.01, 0.92, 0.97],
}

plt.rcParams.update({"font.size": 8, "font.family": "serif"})
fig, ax = plt.subplots(figsize=(3.4, 1.9))
ax.axhspan(0.97, 1.03, color="#2a9d8f", alpha=0.18, lw=0, label="R1 band (0.97–1.03)")
ax.axhline(1.0, color="#2a9d8f", lw=0.8)
rng = np.random.default_rng(0)
for i, (name, r) in enumerate(RATIOS.items()):
    x = i + rng.uniform(-0.12, 0.12, len(r))
    ax.scatter(x, r, s=14, color="#264653", zorder=3)
allr = [v for r in RATIOS.values() for v in r]
no_out = [v for v in allr if v != 0.60]
ax.axhline(np.mean(no_out), color="#e76f51", ls="--", lw=0.9,
           label="mean excl. the 0.60 run")
ax.set_xticks(range(len(RATIOS)), [f"{k}\nn={len(v)}" for k, v in RATIOS.items()])
ax.set_ylabel("phone / OptiTrack speed")
ax.set_ylim(0.55, 1.08)
ax.legend(loc="lower left", fontsize=6.5, frameon=False)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(pad=0.3)
fig.savefig("figures/vio_scale_ratios.pdf")

src = sys.argv[1] if len(sys.argv) > 1 else \
    "/mnt/project-files/velocity-experiment/session-2026-10-26/B_v0.3_r2.png"
img = Image.open(src)
img.crop((0, 30, img.width, 300)).save("figures/vio_example_run.png")
print("ok", len(allr), np.mean(allr), np.std(allr, ddof=1), np.mean(no_out), np.std(no_out, ddof=1))
