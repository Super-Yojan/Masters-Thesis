# ARGOS master's thesis — living report

This folder is the single living thesis report and progress record. It is not a finalized submission.

- `argos_thesis.tex`: main source (imported from the ARGOS LaTeX bundle on Drive, 2026-10-02). The only change from that copy is `\bibliography{../references}` → `\bibliography{references}`.
- `references.bib`: bibliography.
- `argos_thesis.pdf`: compiled PDF (pdfLaTeX + BibTeX, 30 pages).
- `thesis_outline.tex/.pdf`, `papers_research_questions.md`: earlier outline material, kept for history.

Figures are LaTeX placeholders for now; add real figures under `thesis/figures/`.

Build:

    cd thesis
    pdflatex argos_thesis && bibtex argos_thesis && pdflatex argos_thesis && pdflatex argos_thesis

Papers, notes, figures and slide decks moved to the Obsidian vault (`Projects/Masters Thesis/`).
