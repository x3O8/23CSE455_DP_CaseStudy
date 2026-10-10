# Repair review and evidence status

Starting repository HEAD: `ce01bfaa2cb38a27896c7cd0b23626b7745db2d2`, confirmed equal to remote HEAD. No historical commits were created. The final application source is retained unchanged; the fix concerns evidence, reconstructed checkpoints, documentation and verification tools.

## Fresh Rails verification

A new isolated PostgreSQL cluster was initialized inside the workspace and used on loopback port 55433. Each checkpoint and final application used its own Gemfile/lockfile, Ruby 2.7.5 and installed gems. Databases were separately created/migrated. The actual receipts report original 5/0, Change1 13/0, Change2 21/0, Change3 36/0, final 36/0 (examples/failures). All final migrations applied. Duplicate net/protocol constant warnings remain in the logs.

An initial runner invocation discovered zero examples despite exit zero. That was not accepted as a test pass: the runner now explicitly passes `spec` and rejects an empty example result. The successful receipts were rerun with this correction.

The baseline lockfile lacks the Windows platform; Bundler adjusted it during the original run. This was detected by checkpoint verification. Source lockfile bytes were restored, and the runner now restores both schema and lockfile after each execution. The original model test run used Bundler's Windows platform resolution of the retained dependency requirements; it does not prove that the unchanged upstream lockfile installs on every platform or that baseline eager loading succeeds.

## Independent review

A separate reviewer inspected the source reconstruction, validators, metric evidence, tests and UML. Findings were: lockfile mutation during testing (P1), missing review record (P2), and missing automated metric consistency validation (P2). The lockfile restoration and review record are implemented. `check_part2.py` now checks application-file coverage, source hashes, SLOC, metric aggregates and report/slides table values; Ruby Ripper regeneration supplies the metric computation itself. The reviewer found current metric hashes/totals correct and the structural stage dependency repair sound.

## Input access limits

The user supplied DP_Csestudy-2.pdf and DP_Csestudy-3.pdf from Downloads. Both were read completely and all seven pages inspected. `assignment_compliance.md` maps the Part2 requirements, source/evidence coverage, conflicting layout instructions and historical/administrative gaps. The Part2 report now has per-change acceptance/before/after/technique/test/metric records and participant/observation counts. A team README documents source, scope, versions, commands and limitations. The initial repair retained user-requested mirrors; the later grading-risk instruction resolves the conflict by removing repeated inventories and using data/ alone.

The named earlier `A7_Part2_Documentation_and_Snapshot_Fix.zip` has not yet been located or supplied. Its contents and compatibility with HEAD are unassessed. The retained `A7_submission.zip` in a separate old workspace is a different package and is not substituted for the requested ZIP.

## Completed document review

The corrected report (27 pages) and slides (12 pages) compiled with the retained Tectonic 0.15 compiler and cached resources. An initial attempt with a different compiler lacked cached inputenc.sty and failed; it was not treated as a successful build. All 39 rendered pages were inspected using seven contact sheets, with full-size inspection of the changed diagram/metrics pages. No clipping or overlapping content was observed. The compiler reports underfull-box/fontconfig warnings; visible text, diagrams, tables and slide page counts render correctly. The report's source-backed metrics use explicit elsif branch counting: method CC totals are 127, 145, 154 and 171.

The independent reviewer rechecked all three initial findings and confirmed they are resolved, with no remaining substantive issue in that source/evidence scope. A further assignment-based review covers the new documentation/count additions. The earlier fix ZIP remains unavailable. Final compiler/render/page-count and package evidence supersedes the earlier 27/12-page rendering described above after the assignment additions are rebuilt.

The assignment-aligned rebuild compiled successfully: report 29 pages and slides 13 pages. All 42 pages were inspected using eight contact sheets, with full-size checks of changed Part2 acceptance/count/metric pages. No clipping or overlap was observed. The independent assignment-focused review found no new substantive findings; participant mappings, observation totals and requirement coverage are consistent with source. Current PDF hashes and review status are in test_result/pdf_review_manifest.json.

## Grading-risk follow-up review

Experiment 07 retains the genuine exact prompt and raw reviewer response; the reviewer confirms the saved response matches. GPT-6 family is known from system context, while deployment alias/tier remain unavailable. User corrections predate the experiment; subsequent human acceptance is not claimed. The faculty default tree was checked and submission/screenshot remain pending under the user's statement that they will submit later.

The independent follow-up found one P2: eight language READMEs still referenced the removed cross-language CSV mirror. All eight now point to data/cross_language.csv; check_csv validates those README references to prevent recurrence. Other canonical-only datasets, focused source bounds, revised wording and experiment disclosures passed the reviewer's read-only check. Checkpoint and final Rails sources remain unchanged.

The grading-risk report rebuild succeeded under the canonical A7_Report.pdf name (29 pages); the 13-page slides PDF is unchanged. All 42 rendered pages were inspected through eight contact sheets, with full-size checks of changed report pages 16 and 25. No observed clipping or overlap. Current hashes/review receipt supersede earlier document builds.

The independent reviewer confirmed the P2 README finding resolved: all eight references use data/cross_language.csv, and the new validator checks passed with zero CSV/report failures. Final application and checkpoint sources were not modified or regenerated in this follow-up. Existing Rails receipts are retained; no new Rails execution is claimed.
