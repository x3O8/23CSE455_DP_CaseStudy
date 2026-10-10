# Part 2: reproducible requirement evolution

The repair starts at repository HEAD `ce01bfaa2cb38a27896c7cd0b23626b7745db2d2`, verified against remote HEAD. `code/` remains the final working Rails application. Upstream baseline provenance is retained in `../code/SOURCE_PROVENANCE.md` and its 170-file SHA-256 manifest; the added provenance note makes 171 baseline checkpoint files.

## Checkpoint provenance

The repository did not retain separate commits or complete intermediate sources for Change1 and Change2. `checkpoints/original/` copies the retained baseline; `checkpoints/Change3/` copies the final application. Change1 and Change2 are **reconstructed pedagogical checkpoints**, generated from those endpoints by `../tools/rebuild_part2.py`. They are not historical commits. Migration timestamps are retained identifiers, not evidence of execution dates. No historical prompts, model identities, dates, metrics or test results are inferred.

| Checkpoint | Cumulative content | Pattern inventory |
|---|---|---|
| original | Retained upstream application and provenance note | Template Method: 1 |
| Change1 | AdditionalService subclasses, BookingService selections, pricing/payment refresh; bundle/eager-loading support | Template Method: 1 |
| Change2 | Change1 + RoomUpgrade, original-room association, active-reservation availability | Template Method: 1 |
| Change3 | Change2 + refund Strategy, server configuration, authorized cancellation route, refund persistence | Template Method: 1; Strategy: 1 |

Keep `../code/` immutable. Change3 must match `code/` byte for byte excluding runtime files. `checkpoint_manifest.json` hashes every checkpoint file, including configuration, migrations, specs, assets and dotfiles. Runtime logs, storage and caches are excluded; `.keep` files remain.

### Booking.active belongs to Change2

The baseline already has `canceled_at` and `Booking#cancel!`. Change2 introduces `Booking.active`, uses it in RoomUpgrade and Booking availability validation, excludes canceled reservations in `Room#booked_dates`, and rejects upgrades of canceled bookings. It therefore works without Change3. Change3 consumes those semantics and adds calculated-refund policies. Correcting this attribution does not change the final runtime code.

## Reproduction

From the repository root, with Python 3 and Git:

```text
python A7/tools/rebuild_part2.py
python A7/tools/check_part2.py
python A7/tools/check_csv.py
python A7/tools/check_submission.py
python A7/tools/measure_part2.py --ruby /path/to/ruby
python A7/tools/summarize_part2.py
```

Each `changes/ChangeN/diff.patch` is a true adjacent-checkpoint unified patch; `diff.md` explains its boundary. Patches normalize text line endings to LF; the manifest preserves original bytes. The checker verifies the reconstruction recipe and manifest, then actually applies each patch and compares the resulting tree with the next checkpoint.

The count CSV copies in `../data/`, `../Part1/`, and this directory contain the same four-stage inventory. Filter `source_version` for the baseline; Part1 does not claim later patterns as baseline findings. Evolution CSV rows reference each checkpoint's own sources and valid line bounds.

## Rails verification

Use Ruby 2.7.5, Bundler, PostgreSQL and each checkpoint's own Gemfile/lockfile. From a checkpoint, install its bundle, configure the database and run `bin/rails db:create`, `bin/rails db:migrate`, then `bundle exec rspec spec --format documentation`.

The optional Windows runner creates separate test databases and records actual commands, output and exit codes:

```powershell
./A7/tools/run_part2_tests.ps1 -Ruby /path/to/ruby.exe -GemHome /path/to/gems -DatabaseHost 127.0.0.1 -DatabasePort 5432 -DatabaseUser postgres -Stage all
```

Point it at an isolated test server. It never drops databases. Names are `a7_part2_<stage>_test` for original, Change1, Change2, Change3 and final. Schema dumps are restored afterward to preserve checkpoint bytes. The baseline bundle lacks the final eager-loading dependency correction; original model tests do not prove full eager-loading success.

Existing receipts are retained artifacts, not fresh execution proof. Fresh receipts live in `verification/`. Final source includes 5 baseline model, 7 additional-service, 8 upgrade, 9 cancellation service, 6 cancellation request and 1 eager-loading examples. Report actual run counts, including failures. Production behavior, external payment/webhook delivery and concurrency under load are outside these checks.

## Metrics and editable UML

`metrics/before_after.csv` records measured per-file and aggregate SLOC, method count, method CC and a bounded coupling proxy. `ruby_ast_metrics.json` records hashes, method names/lines and explicit dependencies. `metrics/README.md` defines the counting rules and limits. Added functionality increases total size and complexity; responsibility extraction is not evidence of an overall numeric reduction.

Editable PlantUML sources are `diagrams/*.puml`. Render with `java -jar plantuml.jar -tpng A7/Part2/diagrams/*.puml`. BookingService captures a type string; it has no Active Record association to AdditionalService. Cancellation stores a calculated refund and makes no Stripe refund transfer. Services and upgrades are domain modeling and responsibility extraction, not new GoF patterns.

Historical LLM files retain their disclosed transcript and metadata gaps. The supplied assignment PDFs have now been checked: `verification/assignment_compliance.md` maps requirements and documents conflicts/gaps. `evidence/snapshot_summary.csv` adds concrete participant, unique-symbol and rejected/uncertain observation counts. These are current source-review records, not historical events. The earlier named ZIP remains unavailable; access/review status is recorded in `verification/review.md`.
