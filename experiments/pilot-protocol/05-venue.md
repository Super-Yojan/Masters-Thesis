# Venue (Q12, not decided)

Pick **one** primary venue for the pilot and label every trial with it. Results
from different venues are reported in separate tables.

| | Zorvane NEXT field (simulation) | Field 3 practice session (real rovers, NEXT rules) | Actual NEXT match |
|---|---|---|---|
| Same conditions every trial | Yes: fixed bucket seed (`TERRA_NEXT_SEED`), fixed lighting, no weather | Mostly: GPS and heading quality vary with weather and time; heading must be locked by a straight drive each trial | No: an opposing alliance, tagging, and the match clock change every minute |
| Fleet size N > 1 | Yes, 0–32 rovers from the menu or `P/fleet/size` | Only as many rovers as are field-ready (**Q6**) | Same as practice |
| L4 available | Yes, in Local navigation mode (the same `explore_refusal` applies in GPS mode; check in dry run) | Only in Local navigation mode (`explore_refusal`) | Same |
| Trials per day | Many; reset in seconds | Few; battery, setup, field access | One match |
| Ecological validity | Low: idealised sensors, GPS and physics (thesis Ch4) | High for the thesis claim ("real-world, NEXT-style search and rescue") | Highest, but not repeatable |
| Risk to the pilot | Low | Medium: hardware faults end trials | High: one chance, no repeats, competing goals (winning vs protocol) |
| Ethics / safety | Desk study | Spotter, boundary, field permission | Competition rules also apply |

**Draft recommendation:** Zorvane as the primary pilot venue in November, because
the pilot's job is to prove the protocol and logs, and only the simulator gives
repeatable trials and N > 1 next week. Run Field 3 practice sessions as a
separately labelled real-rover block once the simulator pilot is clean, at N = 1
unless more rovers are ready. Do not collect study data during the actual match;
use it, if at all, as a labelled demonstration.

The trade-off against this: the ARGOS design notes call the intended experiment
real-world with simulation for development only (`ch2_competition.tex`
§`sec:real-world`). If Yojan wants the pilot to be real-world from the start,
Field 3 practice at N = 1 is the alternative, and fleet size becomes a later block.
