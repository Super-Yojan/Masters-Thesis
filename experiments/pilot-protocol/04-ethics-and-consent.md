# Ethics and permission path (pilot, draft)

Nothing here is a ruling. Only the university's IRB office (or the office that
makes human-subjects determinations) can say whether the pilot needs review.
The checklist is what to settle, and with whom, **before** any operator other
than Yojan sits at ARGOS for data that will appear in the thesis.

## Q11. Who operates in the pilot? (not decided)

| Option | What it usually means for review (check locally) |
|---|---|
| Yojan only, as a system check | Usually not human-subjects research: no participants, data is about the system. Still state in the thesis that the dry-run data is the author's own. |
| Team members or classmates, data used in the thesis | Usually human-subjects research, because the thesis reports their behaviour and workload (TLX). Typically needs at least an exempt determination before collection. |
| Recruited operators (study proper) | Needs review before recruitment. |

## Checklist

- [ ] Ask the advisor whether the department requires its own sign-off in addition to the IRB.
- [ ] Contact the IRB office and ask for a determination for a minimal-risk operator study (desktop interface, small rovers on a sports field or in simulation, a questionnaire). Ask specifically whether a pilot with classmates needs the same review as the main study.
- [ ] Confirm whether CITI (or equivalent) human-subjects training is required for Yojan and the advisor, and complete it.
- [ ] Decide what is recorded: logs only, or also screen capture, FPV video, audio, think-aloud. Each added stream may change the review category. Draft: logs + TLX only.
- [ ] Decide identifiers: pseudonymous operator IDs (P01, P02…). The ID-to-name key is kept apart from the logs, off git.
- [ ] Decide storage: where raw logs live (university storage vs personal laptop), who has access, how long they are kept.
- [ ] Decide what goes in the public repo: aggregated tables only, or de-identified per-trial logs.
- [ ] Physical safety (field venue): a spotter who can stop any rover, a field boundary, no bystanders within the operating area, permission to use Field 3 outside the match.
- [ ] Compensation, if any, and whether course credit or grades are involved (classmates must not feel obliged).
- [ ] Get the determination letter (or exemption) in writing and record its number in the thesis methods.
- [ ] Do not start operator trials with anyone except Yojan until the above is settled. If it is not settled by Oct 31, run the Nov week 1 dry runs with Yojan only and slip the operator pilot.

## Draft consent text (to adapt to the IRB template)

> **Supervising robots from one operator station: pilot study**
>
> **Researcher:** [name, program, university]. **Advisor:** [name].
>
> **What you will do.** You will use a desktop program to supervise one to three small wheeled robots, either in a computer simulation or on a sports field, while they cover an area. You will try several ways of controlling them, from driving by keyboard to letting the robot explore on its own. Each trial lasts about 10 minutes, and the session takes about [90] minutes including practice and short questionnaires.
>
> **What is recorded.** The program records the commands you send, when you send them, and what the robots do. After each set of trials you will fill in a short workload questionnaire. [No video or audio of you is recorded.] Your name is not stored with the data; you are identified by a code.
>
> **Risks.** The risks are no greater than using a computer program. On the field, the robots are small and slow, and a researcher can stop them at any time. You may feel some frustration if a robot gets stuck.
>
> **Benefits.** There is no direct benefit to you. The results will help design robot systems that one person can supervise.
>
> **Voluntary.** Taking part is voluntary. You may stop at any time without giving a reason, and you may ask for your data to be removed until [date]. Whether you take part has no effect on any grade or standing.
>
> **Data.** De-identified data may be published in a thesis, papers, and a public code repository. [Storage and retention statement from the IRB template.]
>
> **Contact.** Questions about the study: [email]. Questions about your rights as a participant: [IRB office contact].
>
> I have read this information and agree to take part. ______________________ Date ________
