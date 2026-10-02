# Masters thesis — phone-brain multi-robot fleets

Cheap multi-robot autonomous fleets for disaster recovery (also military surveillance, fire/rescue): consumer phones as sensor/brain/compute on rolling chassis, collaborative mapping, and a one-human multi-fleet command interface.

Academic writing and software live in separate trees. Drafts and the thesis outline stay under `papers/` and `thesis/`. Application and robot code goes under `src/`.

## Layout

| Path | What belongs here |
| --- | --- |
| [`papers/`](papers/) | One folder per paper: LaTeX drafts and tracked PDFs |
| [`thesis/`](thesis/) | Thesis outline and the three-paper research questions |
| [`src/`](src/) | Phone app, planners, and drivers (placeholder; no code yet) |
| [`hardware/`](hardware/) | Chassis, mounts, CAD, and hardware notes |
| [`experiments/`](experiments/) | Logs, run configs, and evaluation scripts |
| [`docs/`](docs/) | Short architecture notes for the software stack; current ARGOS / Terra platform summary: [`docs/ARGOS_CURRENT_SUMMARY.md`](docs/ARGOS_CURRENT_SUMMARY.md) |

## Writing

- [`thesis/thesis_outline.tex`](thesis/thesis_outline.tex) — working LaTeX outline; compiled export is [`thesis/thesis_outline.pdf`](thesis/thesis_outline.pdf)
- [`thesis/papers_research_questions.md`](thesis/papers_research_questions.md) — research questions and evaluation metrics for the three-paper spine
- [`papers/paper1-phone-as-brain/`](papers/paper1-phone-as-brain/) — Paper 1 draft (introduction and problem formulation), with `introduction.pdf` and `problem_formulation.pdf`
- [`papers/paper2-collaborative-slam/`](papers/paper2-collaborative-slam/) — Paper 2 placeholder
- [`papers/paper3-fleet-dashboard/`](papers/paper3-fleet-dashboard/) — Paper 3 placeholder

## Three-paper spine

1. [Phone-as-brain feasibility](papers/paper1-phone-as-brain/) (single rover) — introduction and problem formulation in draft
2. [Multi-phone collaborative SLAM / shared maps](papers/paper2-collaborative-slam/)
3. [One-human multi-fleet collaboration dashboard](papers/paper3-fleet-dashboard/)

## Adding code

Put new software in [`src/`](src/README.md): the phone app, local planners, and chassis drivers. Hardware notes go in [`hardware/`](hardware/README.md). Run logs, configs, and eval scripts go in [`experiments/`](experiments/README.md). Short architecture notes go in [`docs/`](docs/README.md).

## Status

Working draft materials. Not a final thesis document. Application code is not in this repository yet.
