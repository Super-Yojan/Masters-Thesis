# Paper 1 — Phone-as-brain feasibility

**Status:** first draft. Introduction and problem formulation only. Methods, experiments, and results are not written yet.

**Research question:** Can a consumer phone (app + cameras/IMU/compute) run the sensing and control loop for a cheap differential-drive rover well enough for waypoint navigation with local obstacle avoidance, without onboard industrial compute?

## Files

- `introduction.tex` — motivation (cheap fleets for disaster recovery and related response tasks), the phone-only gap, and a three-item contribution preview.
- `problem_formulation.tex` — system, waypoint task, loop-rate and latency requirement, decision problem, and scope.

Both files are standalone LaTeX articles. The preamble matches `thesis_outline.tex`. From this directory:

```bash
pdflatex introduction.tex
pdflatex introduction.tex
pdflatex problem_formulation.tex
pdflatex problem_formulation.tex
```

Compiled exports (two `pdflatex` passes so citations resolve):

- [introduction.pdf](introduction.pdf)
- [problem_formulation.pdf](problem_formulation.pdf)

The thesis outline export is [thesis_outline.pdf](../../thesis_outline.pdf) at the repository root. Build junk (`*.aux`, `*.log`, and the rest) stays ignored; these PDFs are tracked.

Metrics match `papers_research_questions.md`: loop rate and latency, waypoint success, obstacle clearance, interventions and e-stops, power and thermal limits, and cost and setup time against a dedicated-compute baseline.

Scope of this paper is one rover. Multi-robot SLAM and the fleet HUD/VR/AR interface belong to Papers 2 and 3. Differential-drive kinematics and the DWA objective are named here and deferred to a later methods section.
