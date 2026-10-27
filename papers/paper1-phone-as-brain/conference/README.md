# Conference draft: Is a Phone Enough?

**Working title:** Is a Phone Enough? Measuring an iPhone as a Ground Robot's Only Sensor Head and Computer

**Status (2026-10-27):** first full draft, 6 pages in the IEEE conference template. Results for R1–R5 are filled from data. R6–R9 and the follow-up runs are red `\todo{}` markers. No number in the draft is estimated.

**Source:** thesis Chapter 6 ([`thesis/chapters/ch6_phone_platform.tex`](../../../thesis/chapters/ch6_phone_platform.tex), PRs #18–#20) and the VIO table in Ch5 (`sec:auto-state-validation`).

## Contributions

| # | Contribution | Section | Data |
| --- | --- | --- | --- |
| 1 | Requirements R1–R9 on the phone, each tied to the part of Terra that uses it | IV | Terra constants |
| 2 | ARKit VIO vs OptiTrack on a skid-steer rover with no wheel encoders (17 runs) | V | Mocap sessions Oct 26–27 |
| 3 | Per-hop sensor timing probe that blames each stale tick on iOS or the app; iOS IMU p99 ≤ 2.3 ms, stalls came from the Debug build | VI | Sensor-timing runs Oct 27 |

## What is still missing (in paper order)

| TODO | Needed for | Experiment |
| --- | --- | --- |
| Affiliation, email, rover dimensions and bill of materials | Sec. III | – |
| Scale away from the mocap room, 120 runs | R1 | E1b |
| Yaw rate in arcs against OptiTrack | R4 | E1c |
| ≥10 min Release run with full load | R5 | E2 |
| Same probe while driving | R5 | E2 C5 |
| LiDAR obstacle range and false obstacles | R6 | E3 |
| Real buckets at 2–12 m, sun and shade | R7 | E4 |
| GNSS CEP95 on the field, compass near motors | R8 | E5 |
| 90 min endurance, battery and thermal | R9 | E6 |
| Code and data release statement, acknowledgments | – | – |

## Target venues (checked 2026-10-27)

| Venue | Deadline | Fit | Notes |
| --- | --- | --- | --- |
| **IROS 2027**, Florence, Sep 26 – Oct 1, 2027 | **Mar 1, 2027** | Best fit: systems + field robotics | Deadline from the IEEE RAS deadline calendar and BERI listing; the official CFP is not up yet. 6 pages + 2 extra paid pages is the usual IROS format; confirm. |
| **IEEE RA-L** (journal, can be presented at IROS 2027 or ICRA 2028) | Rolling; the IROS option deadline is usually a few days before the IROS deadline | Good if E1b–E6 make it a journal-sized result | 6 pages + 2 extra; same template. |
| **IEEE CASE 2027** | **Mar 1, 2027** | Backup: low-cost automation angle | Deadline from the IEEE RAS calendar. |
| ARSO 2027, Mountain View, Mar 13–15, 2027 | Dec 1, 2026 | Weaker fit (social impact of cheap robots) | Only realistic if the paper goes out with R6–R9 still pending. |

ICRA 2027's paper deadline (Sep 2026) has passed. ICRA 2027 workshop paper calls are not out yet; they usually close in spring.

Sources: [IEEE RAS deadline calendar](https://www.ieee-ras.org/events/category/deadlines/), [BERI IROS 2027 listing](https://www.beri.net/events/iros-2027), [ICRA 2027 CFP](https://2027.ieee-icra.org/announcements/call-for-technical-papers/), [ARSO 2027 deadline](https://www.ieee-ras.org/event/deadlines-paper-submission-deadline-arso-2027-ieee-international-conference-on-advanced-robotics-and-its-social-impacts-arso-28145-0/).

## Files

- `main.tex` — the paper (IEEEtran, conference mode).
- `references.bib` — the phone-as-robot block of `thesis/references.bib`. Page numbers the thesis marked VERIFY were dropped here, not guessed. Li & Mourikis 2014 (IJRR 33(7):947–964) was checked against the author's page. Still unverified: OpenBot pages, Delmerico 2018 pages, Stisen 2015 pages.
- `figures/phone_timing_*.pdf` — copied from `thesis/figures/` (made by `make_figures.py` in the sensor-timing project folder).
- `figures/vio_scale_ratios.pdf`, `figures/vio_example_run.png` — made by `make_vio_figures.py` from the Ch5 ratio table and the session-1 analysis plot.
- `main.pdf` — compiled draft.

## Build

```bash
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

Needs `texlive-publishers` (IEEEtran), `texlive-latex-extra`, `texlive-pictures`.
