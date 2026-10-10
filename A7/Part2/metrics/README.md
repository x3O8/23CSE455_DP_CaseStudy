# Source-backed before/after metrics

Generated from `app/**/*.rb` in each retained checkpoint by Ruby Ripper. Every per-file row has a SHA-256 and exact source path. No historical metric values or timing results are inferred.

| Stage | SLOC | Methods | Sum method CC | Max method CC | Explicit app references (sum) |
|---|---:|---:|---:|---:|---:|
| original | 495 | 95 | 127 | 4 | 27 |
| Change1 | 556 | 105 | 145 | 5 | 31 |
| Change2 | 596 | 110 | 154 | 6 | 31 |
| Change3 | 654 | 121 | 171 | 6 | 35 |

SLOC counts nonblank lines excluding lines whose first nonwhitespace character is `#`; inline comments count with their code. Method CC is 1 plus AST decisions (`if`, `elsif`, `unless`, modifier forms, `while`, `until`, `for`, ternary, each `when`, each `rescue`, and boolean `&&`, `||`, `and`, `or`). Blocks are traversed within their enclosing method; top-level decisions are excluded. This stated convention is reproducible and is not a claim of compatibility with every CC tool.

Coupling proxy: distinct explicitly referenced application-owned constants per source file, excluding its declarations, strings, Rails/gem constants and dynamic association names; the aggregate is the sum of file counts. It omits implicit Rails and runtime dispatch dependencies, so it is not full CBO. `ruby_ast_metrics.json` records referenced constants and method names/lines/CC.

The new requirements increase total source size, method count and explicit dependencies. Responsibility extraction and Strategy do not imply a numeric reduction in whole-application complexity. Compare Booking and BookingsController rows with the new services to see where responsibilities move. These checkpoints are cumulative, so metrics compare growing functionality rather than equivalent implementations.
