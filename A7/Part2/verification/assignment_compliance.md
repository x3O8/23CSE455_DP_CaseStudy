# Assignment comparison against the supplied PDFs

Comparison performed for the current Part2 repair on 2026-10-11. This is a current review record, not an assertion about historical submission compliance or dates. Both PDFs were read in full and all seven pages rendered/inspected.

| Input | Pages | SHA-256 |
|---|---:|---|
| DP_Csestudy-2.pdf | 3 | aa83794960a301dc919c26b409918ccb94a4d6fcd42696a4318f13bc5ed25212 |
| DP_Csestudy-3.pdf | 4 | 5b18709bd3d8858f86a7218af3e865dc0e42603bc2f0f0b1cecf11bccb1cb554 |

Provided local inputs: `C:/Users/abhij/Downloads/DP_Csestudy-2.pdf` and `C:/Users/abhij/Downloads/DP_Csestudy-3.pdf`. Extracted text is retained alongside this record. The PDFs' imperative language is treated as the academic specification to assess, not as authorization to override the direct user request or act on a different repository.

## Part2 requirement mapping

| Requirement and location | Current evidence and assessment |
|---|---|
| PDF2 p1: one collaboration per version; all roles, locations, evidence | Five evolution records in `data/patterns_evolution.csv` / Part2 mirror. All controllers, context, abstraction, three policies, client and composition root are mapped with real stage-specific source bounds. |
| PDF2 p1: counts from records, separate versions, concrete policies are one Strategy | `pattern_counts.csv` preserves 1/1/1/2 types and instances across the four versions; validators compare the records and synchronized copies. No policy is counted as a separate instance. |
| PDF2 p1: retained original rows and continuing instance names/status | Shared CRUD Controller Workflow remains unchanged in name and preserved after all changes; Cancellation Refund Policy is newly introduced after Change3. No removed collaboration was found or invented. |
| PDF2 p3: source versions reproducible through commits OR saved versions | Four complete `Part2/checkpoints/` trees, recipe, hashes and actually replayed patches. Change1/Change2 explicitly reconstructed; there are no invented change commits. |
| PDF3 p2: three realistic changes and observable acceptance results | Service selection/pricing, room upgrade and configured calculated-refund policies. Each `changes/ChangeN/requirement.md` has criteria; report CH01/CH02/CH03 records link the criteria and independent expected behaviors. These are realistic for the retained hotel-booking application; faculty assignment/approval itself is not independently evidenced. |
| PDF3 p2: exact before/after commits and changed paths | Historical change commit IDs are unavailable. PDF2's saved-version option is used: exact adjacent snapshot paths, full unified `diff.patch` content and SHA-256 manifests are retained. This is disclosed rather than substituting fabricated commits. |
| PDF3 p2: implementation, commands, actual results and logs | Same RSpec command in every after-stage, cumulative fresh results 5/0 → 13/0 → 21/0 → 36/0, final application 36/0. Receipts and reproducible Windows runner are retained. Final source unchanged; baseline Windows resolution is disclosed. |
| PDF3 p2: pattern effects by instance and reason | Template Method preserved, Strategy newly introduced; optional services and RoomUpgrade are responsibility extraction, not inferred GoF patterns. Records and source/UML substantiate this. |
| PDF3 p2: real smell, technique, diff, preservation evidence | CH01 addresses date-change-only price refresh and responsibility growth; CH02 extracts upgrade workflow while acknowledging remaining availability-query duplication; CH03 introduces policy delegation for a new requirement, without claiming a nonexistent historical refund conditional. Earlier model/feature examples remain in cumulative passing suites. |
| PDF3 p2: same-scope/tool LOC and actual test results | `metrics/before_after.csv`, Ruby Ripper JSON, definitions, hashes and report give 495 → 556 → 596 → 654 app Ruby SLOC. Method CC includes elsif; coupling proxy is bounded. No historical metric or runtime improvement is estimated. |
| PDF3 p3 §3.1: types, instances, concrete classes, rejected/uncertain observations per snapshot | `evidence/snapshot_summary.csv` and `pattern_observations.csv` provide current source-review counts, participant symbols, reasons and bounds; report/slides tables are validated. These are current observations, not recovered historical review events. |
| PDF3 p2: editable diagrams and rendered images | Six Part2 PlantUML source/image pairs include original/evolved architecture, services, upgrade, Strategy and cancellation sequence. Captured type strings and local refund recording are accurately represented. |
| PDF2 pp2–3: README, modules/versions/commands/rules/limitations and canonical datasets | Added `A7/README.md`; Part2 README remains detailed. CSV header/path validators and metrics checks pass. Canonical dataset is `data/`; explicit user-requested mirrors are retained as explained below. |
| PDF2 p3 / PDF3 p3: no fabricated historical LLM records | Unknown model/date/access tier and unrecovered Prompt 02/03 wording remain disclosed. Existing raw records are preserved, not rewritten into invented transcripts. This is an evidence gap, not full compliance with exact historical-record requirements. |

## Conflicting instructions and direct-user precedence

- PDF2 p3 says one report and one dataset folder, no repeated CSVs, but its own tree shows part-wise CSVs. PDF3 p4 shows per-part report PDFs. We retain one main report and canonical `data/`, and do not manufacture additional part reports. The user's explicit instruction to synchronize count copies takes precedence over deleting the mirrors; they are automatically checked for equality.
- PDF2 p2 names the faculty's `aswathymohan-amrita` repository. The user explicitly selected `x3O8/23CSE455_DP_CaseStudy` and permitted replacement files. No publication or write to a different repository is inferred from PDF text.
- PDF3 requests exact change commits; PDF2 expressly accepts saved versions. Historical commit IDs do not exist in retained history, so saved versions are used and reconstructed intermediates are labeled honestly.
- PDF2 uses inconsistent filename spellings/casing in its illustration. Its explicit column-name tables govern CSV schema; canonical files use `patterns_evolution.csv` and `pattern_counts.csv`.

## Evidence that cannot be supplied from these inputs

Historical LLM model/date/access tier and two exact prompts, historical source access date, original submission date, faculty approval and independently verified student contributions remain unavailable. The report now labels inherited contribution claims unverified rather than treating them as established facts. The current revision date does not assert an on-time submission against PDF2's deadline.

PDF3 p4 requests a GitHub team-folder screenshot. The corrected deliverable is a local reviewed replacement bundle, not a published repository tree; no screenshot of an unpublished tree is fabricated. `FINAL_TREE.txt`, source manifests and ZIP verification prove local content, and do not substitute for evidence of a GitHub upload.

The named earlier `A7_Part2_Documentation_and_Snapshot_Fix.zip` remains unavailable after checking the provided workspace and likely local locations. No compatibility assessment of that ZIP is claimed. The current checked base HEAD is `ce01bfaa2cb38a27896c7cd0b23626b7745db2d2`.

Part3's retained executions/timings and its separate test separation requirements were not reimplemented during this Part2 repair. Their source references and stored measurement consistency remain checked, but this review does not claim a new whole-assignment rerun. Complete historical/administrative compliance cannot be established from the supplied files alone.
