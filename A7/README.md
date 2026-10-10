# A7 - Design-pattern case study

One report and one canonical dataset folder cover the whole case study. The report is `A7_Final_Report.pdf`, with editable source `A7_Report.tex`; slides are `A7_slide.pdf` / `A7_slide.tex`. Supporting parts are not separate submissions.

| Roll number | Student | Batch |
|---|---|---|
| AM.AI.U4AID23016 | Kavya Penikalapati | AIDS (AI & DS) |
| AM.AI.U4AID23037 | E. Abhijith Krishna | AIDS (AI & DS) |
| AM.AI.U4AID23040 | Guduru Akshaya Giri | AIDS (AI & DS) |
| AM.AI.U4AID23046 | Kurt Sony Rebello | AIDS (AI & DS) |

Names, roll numbers and batch are retained from the supplied report source. Specific historical contribution attribution and faculty approval are not independently verified by the available inputs.

## Application, source and observation scope

Application: Rails Room Booking, a hotel/vacation reservation application. Original source: https://github.com/andrewdsilva/rails-room-booking at `5e15551ee646871b4bed32c982fa17da319d3ee3`, retained in `code/`. That source's README declares MIT licensing; historical access date and separate faculty approval are unavailable. Retained source was inspected for this repair on 2026-10-11. Submission repository being repaired: https://github.com/x3O8/23CSE455_DP_CaseStudy, starting HEAD `ce01bfaa2cb38a27896c7cd0b23626b7745db2d2`.

Inspect `app/models`, model concerns, controllers/controller concerns, policies, application services, routes, initializers, migrations, schema and their specs. Exclude framework/dependency internals from application-owned GoF claims; production infrastructure, remote Stripe/webhook delivery and concurrency under load are not established by local tests. Part2 checkpoints cover the complete application, not just changed snippets.

## Environment and commands

Retained dependencies: Ruby 2.7.5; Rails requirement `~> 7.0.4`, lockfile Rails 7.0.6; Bundler 2.4.17; PostgreSQL. Fresh repair runs used Ruby 2.7.5 on Windows, installed gems and PostgreSQL 15.10 with an isolated test server. Original Windows dependency resolution is disclosed in `Part2/verification/review.md`. Dependency caches, local database files and runtime installation binaries are excluded from the replacement archive.

From `Part2/code/`, install the bundle, set database environment variables from `.env.dist`, then run:

```text
bundle install
bundle exec rails db:create db:migrate
bundle exec rspec spec --format documentation
bundle exec rails server
```

Configure development credentials locally; do not commit them. No external payment credentials are required for the recorded test suite. From the repository root, verify the source/evidence package:

```text
python A7/tools/rebuild_part2.py
python A7/tools/measure_part2.py --ruby /path/to/ruby
python A7/tools/summarize_part2.py
python A7/tools/check_part2.py
python A7/tools/check_csv.py
python A7/tools/check_submission.py
python A7/tools/package_submission.py --output A7_Part2_Reviewed_Replacement.zip
```

See `Part2/README.md` for Windows Rails runner options. Fresh cumulative suites: original 5/0, Change1 13/0, Change2 21/0, Change3 36/0, final app 36/0 (examples/failures). Commands, actual outputs and exit codes are in `Part2/verification/*_rails.txt`. Historical receipts stay separate. These source/evidence updates do not alter baseline or final Rails code.

## Dataset and measurement rules

`data/` is canonical: `patterns.csv`, `patterns_evolution.csv`, `pattern_counts.csv`, `cross_language.csv`, `llm.csv`. All paths are relative to this A7 folder. Pattern counts represent collaborations, not individual concrete strategies. Template Method's shared CRUD collaboration persists across all four snapshots; Cancellation Refund Policy introduces one Strategy collaboration after Change3.

Part2 metrics use the same `app/**/*.rb` scope and Ruby Ripper convention across snapshots. SLOC excludes blank/comment-only lines; method CC is one plus the documented AST decision count. A bounded explicit-constant coupling proxy is not full CBO. Source hashes, method records and limitations are in `Part2/metrics/`. Added requirements increase aggregate size/complexity; LOC alone is not evidence of better design.

Additional participant and current rejected/uncertain observation counts are in `Part2/evidence/snapshot_summary.csv` and `pattern_observations.csv`. A concrete participant means a class implementing a variable pattern role. Shared symbols count once; final symbols include the configured cancellation-policy callable. Counts are current source-review observations, not fabricated historical reviews.

Part3 uses one representative instance of each confirmed pattern, shared inputs and expected output in Java/Python/JavaScript/C++. Its production SLOC, maximum function CC, compiler/runtime and actual commands/results are retained in `data/cross_language.csv` and language READMEs. Timing includes process startup: compile first where applicable, one warmup and five measured processes, median and raw samples retained. Those historical timing runs were not repeated during this Part2 repair; no missing times are estimated.

## Assignment interpretation and limits

`Part2/verification/assignment_compliance.md` maps the supplied PDFs to source/evidence and documents their conflicting layout instructions. The direct user request to synchronize count copies takes precedence over the PDF's no-duplicate-dataset instruction: supporting CSV mirrors are retained and automatically checked; `data/` remains canonical. The user-selected x3O8 repository is not silently replaced by the faculty repository named in the PDF.

Saved versions satisfy reproducibility without invented change commits. Historical LLM model/date/access tier and Prompt 02/03 verbatim wording remain unavailable and disclosed. Faculty approval, actual student contribution evidence and original submission date cannot be inferred. The earlier named fix ZIP is still unavailable. This repair does not assert complete historical compliance where evidence is missing.
