"""Generate source-backed static metrics for all four checkpoints.

python A7/tools/measure_part2.py --ruby /path/to/ruby
Metrics are structural measurements, not runtime benchmarks or quality scores.
"""
import argparse
import csv
import json
import subprocess
from rebuild_part2 import ROOT, PART, STAGES

HEADER = ['stage', 'file', 'sha256', 'source_loc', 'method_count', 'sum_method_cc', 'max_method_cc', 'explicit_app_dependency_count', 'explicit_app_dependencies']


def measure(ruby):
    evidence = PART / 'metrics'
    evidence.mkdir(exist_ok=True)
    detail = {}
    rows = []
    for stage in STAGES:
        result = subprocess.run([ruby, str(ROOT / 'tools/ruby_metrics.rb'), str(PART / 'checkpoints' / stage)], capture_output=True, text=True, check=True)
        files = json.loads(result.stdout)
        detail[stage] = files
        for f in files:
            rows.append([stage, 'Part2/checkpoints/' + stage + '/' + f['path'], f['sha256'], f['sloc'], f['method_count'], f['sum_method_cc'], f['max_method_cc'], len(f['explicit_app_dependencies']), '; '.join(f['explicit_app_dependencies'])])
        rows.append([stage, 'TOTAL app/**/*.rb', '', sum(f['sloc'] for f in files), sum(f['method_count'] for f in files), sum(f['sum_method_cc'] for f in files), max(f['max_method_cc'] for f in files), sum(len(f['explicit_app_dependencies']) for f in files), 'sum of per-file distinct explicit references'])
    (evidence / 'ruby_ast_metrics.json').write_text(json.dumps(detail, indent=2)+'\n', encoding='utf-8')
    with (evidence / 'before_after.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(HEADER); w.writerows(rows)
    totals = [r for r in rows if r[1].startswith('TOTAL')]
    text = '# Source-backed before/after metrics\n\n'
    text += 'Generated from `app/**/*.rb` in each retained checkpoint by Ruby Ripper. Every per-file row has a SHA-256 and exact source path. No historical metric values or timing results are inferred.\n\n'
    text += '| Stage | SLOC | Methods | Sum method CC | Max method CC | Explicit app references (sum) |\n|---|---:|---:|---:|---:|---:|\n'
    text += ''.join('| '+r[0]+' | '+' | '.join(str(v) for v in r[3:8])+' |\n' for r in totals)
    text += '\nSLOC counts nonblank lines excluding lines whose first nonwhitespace character is `#`; inline comments count with their code. Method CC is 1 plus AST decisions (`if`, `elsif`, `unless`, modifier forms, `while`, `until`, `for`, ternary, each `when`, each `rescue`, and boolean `&&`, `||`, `and`, `or`). Blocks are traversed within their enclosing method; top-level decisions are excluded. This stated convention is reproducible and is not a claim of compatibility with every CC tool.\n\n'
    text += 'Coupling proxy: distinct explicitly referenced application-owned constants per source file, excluding its declarations, strings, Rails/gem constants and dynamic association names; the aggregate is the sum of file counts. It omits implicit Rails and runtime dispatch dependencies, so it is not full CBO. `ruby_ast_metrics.json` records referenced constants and method names/lines/CC.\n\n'
    text += 'The new requirements increase total source size, method count and explicit dependencies. Responsibility extraction and Strategy do not imply a numeric reduction in whole-application complexity. Compare Booking and BookingsController rows with the new services to see where responsibilities move. These checkpoints are cumulative, so metrics compare growing functionality rather than equivalent implementations.\n'
    (evidence / 'README.md').write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--ruby', required=True)
    measure(p.parse_args().ruby)
