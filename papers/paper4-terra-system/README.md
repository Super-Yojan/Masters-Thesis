# Paper 4: Terra system paper

**Status:** first full draft (Oct 27, 2026). Architecture, mapping, autonomy ladder, objects and integration are written from the code. The field evaluation is a proposed design; every result is a red `[TODO]` in the PDF. No number in the draft is invented: each one comes from Terra/ARGOS/Zorvane main on Oct 27, 2026, thesis Ch3/Ch5, or the project's Zorvane detector run.

**Working title:** Terra: A Phone-Brained Rover with a Six-Level Autonomy Ladder, from Teleoperation to On-Device Language-Model Tasking

**Scope:** the systems question (how to structure a phone-brained rover so one autonomy stack runs on the phone, in Zorvane and under ARGOS). The sensor evaluation (VIO vs OptiTrack, sensor timing, Debug vs Release, GNSS, endurance) belongs to the companion iPhone sensor paper and is only cited here (`companion2026phone` in `references.bib`, a placeholder to replace).

## Files

- `main.tex`: IEEE conference paper (`IEEEtran`, conference mode), currently 6 pages with TODOs.
- `references.bib`: entries copied from `thesis/references.bib` and the verified LLM multi-robot bib, plus five new ones. Every entry whose note says VERIFY must be checked before submission.
- `main.pdf`: compiled draft.

## Build

```bash
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

Needs `texlive-publishers` (for IEEEtran) besides the thesis packages.

## Candidate venues (checked Oct 27, 2026)

| Venue | Paper deadline | Conference | Fit |
| --- | --- | --- | --- |
| IROS 2027 | Mar 1, 2027 | Sep 26 – Oct 1, 2027, Florence, Italy | Best fit: systems + field robotics track |
| IEEE CASE 2027 | Mar 1, 2027 (full papers) | Aug 23–27, 2027, Linz, Austria | Good fit for a systems/automation paper with a smaller field study |
| IEEE RA-L | Rolling | Journal letter, 8 pages | If the field campaign is strong; check whether an IROS 2027 presentation option exists |

Sources: [IEEE RAS deadlines](https://www.ieee-ras.org/events/category/deadlines/), [IROS 2027](https://www.beri.net/events/iros-2027), [CASE 2027](https://www.beri.net/events/ieee-case-2027). ICRA 2027 (deadline Sep 16, 2026) has already closed. Re-check each official CFP before committing.

## Open items before submission

1. Run the field campaign F1–F7 (Section IX of the draft); size runs after a pilot day.
2. Run L5 end to end on an iOS 26 phone.
3. Add 2–3 recent (2024–2026) phone-robot systems to related work.
4. Bill of materials table, affiliation, acknowledgments.
5. Replace the companion-paper placeholder citation.
