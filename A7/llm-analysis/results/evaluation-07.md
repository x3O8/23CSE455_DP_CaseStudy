# Experiment 07 evaluation and verification

This is a new interaction on 2026-10-11 Asia/Calcutta using the session's system-identified GPT-6 family through the existing Codex review agent. The exact deployment alias, access tier and reasoning setting are not exposed; no commercial/public-free model label is invented. Metadata records those limits. The exact dispatched prompt, frozen primary inputs, their source hashes and unchanged response are retained. The agent inherited earlier review history, so this is not a blind independent model trial.

## Actual human corrections supplied before the experiment

The user supplied these instructions verbatim in the grading-risk list:

> Replace the inaccurate claim that additional-service pricing was moved from existing controller branching. It was introduced as a separate responsibility.

> Remove the claim that `RoomUpgrade` avoids changes to `Booking#cancel!`. Explain its actual responsibility: availability, price difference and room reassignment.

These are the human corrections that motivated this experiment, not invented human feedback after it. The remaining evaluation below is performed by Codex. Student/faculty acceptance of the new response is pending.

## Specific AI claims, disposition and evidence

| Raw response claim | Codex evaluation / applied correction | Verification |
|---|---|---|
| 1 rejects pre-existing controller pricing branches | Accepted; Change1 diff.md now describes newly introduced pricing responsibility. | Baseline BookingsController#cancel 6–14; CrudConcern#create 28–40 and #update 48–60. AdditionalServicePricing.total 2–4 and Change2 Booking#compute_price_ht 73–75 / #add_service 77–79. |
| 2 calls leaving cancel! unchanged narrowly supported | Its narrow byte/body observation is accurate, but the user-required causal/design claim is misleading. Removed it from the report. RoomUpgrade owns availability, nightly price difference, room reassignment and saving. | RoomUpgrade#call 9–28, #available? 32–34, #price_difference 36–39. Baseline cancel! 59–61 / Change2 65–67 are the same operation; no old upgrade branch is evidenced. |
| 3 assigns active scope to Change2 | Accepted; no code changes. | Change2 Booking scope line 15 and #dates_are_available 25–31; RoomUpgrade#available? 32–34. check_part2 verifies the stage boundary. |
| 4 identifies one Strategy collaboration and local refund recording | Accepted; three policies are alternatives, not three instances. | CancellationService#initialize 2–5 / #call 7–16; CancellationPolicy and concrete methods; BookingsController#cancel 7–21 and initializer 2–10. Canonical evolution CSV now qualifies each method with focused bounds. |
| 5 treats 13/21/36 zero-failure counts as recorded receipts | Accepted with the stated limit: no tests were executed by the experiment agent. | Change1_rails.txt 118/120; Change2_rails.txt 66/68; Change3_rails.txt 157/159. Existing full final receipt remains 36/0. |

All source references above are from the numbered frozen input context, whose captured files and hashes are listed in input-07-source-hashes.json. Precise qualified evidence lives in data/patterns_evolution.csv. Frozen Change1/diff.md intentionally contains the original inaccurate statement so the response can be evaluated; its hash may differ from the corrected live document. Executable source and receipts were not altered. Exact raw response was saved separately rather than edited to match this evaluation.

The validator checks prompt equality with the Part2 wrapper, metadata date/model limits, all evidence paths, artifact SHA-256 values and frozen input sections. Source/stage/metric/patch checks and CSV/report checks are rerun in this revision; their receipts are retained under Part2/verification and test_result. They establish document/data consistency, not historical commits, new Rails runs, human approval or external payment behavior.
