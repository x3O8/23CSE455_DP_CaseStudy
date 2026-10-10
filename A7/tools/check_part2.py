"""Check checkpoint bytes, patch replay, stage dependencies and generated CSVs.

No Rails/database access. Does not update evidence files: redirect stdout explicitly.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import csv
from rebuild_part2 import ROOT, PART, STAGES, tree, checkpoints, unified


def verify():
    expected = checkpoints()
    manifest = json.loads((PART / 'checkpoint_manifest.json').read_text())
    for stage, files in zip(STAGES, expected):
        actual = tree(PART / 'checkpoints' / stage)
        assert actual == files, f'{stage}: checkpoint differs from reconstruction recipe'
        assert manifest['stages'][stage] == {p: hashlib.sha256(b).hexdigest() for p, b in files.items()}, f'{stage}: manifest differs'
        print(f'PASS {stage}: {len(actual)} files match recipe and SHA-256 manifest')
    assert tree(PART / 'checkpoints/Change3') == tree(PART / 'code'), 'Final checkpoint differs from live application'
    assert b'scope :active' not in expected[1]['app/models/booking.rb']
    assert b'scope :active' in expected[2]['app/models/booking.rb']
    assert b'.bookings.active' in expected[2]['app/services/room_upgrade.rb']
    assert not any('cancellation_policy' in p for p in expected[2])
    print('PASS Booking.active introduced in Change2 before use; Change3 only introduces refund Strategy')
    temp_root = ROOT.parent / '.verification'
    temp_root.mkdir(exist_ok=True)
    for i, stage in enumerate(STAGES[1:], 1):
        patch = PART / 'changes' / stage / 'diff.patch'
        assert patch.read_text(encoding='utf-8') == unified(expected[i-1], expected[i]), f'{stage}: patch not current'
        with tempfile.TemporaryDirectory(prefix='patch-', dir=temp_root) as directory:
            for p, b in expected[i-1].items():
                dest = Path(directory) / p
                dest.parent.mkdir(parents=True, exist_ok=True)
                # Unified patches represent logical text lines (LF), not OS newline bytes.
                dest.write_bytes(b.replace(b'\r\n', b'\n'))
            for flags in [['--check'], []]:
                env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(temp_root.resolve()))
                result = subprocess.run(['git', '-c', 'core.autocrlf=false', 'apply', '--no-index', '--whitespace=nowarn', *flags, str(patch.resolve())], cwd=directory, env=env, capture_output=True, text=True)
                assert result.returncode == 0, f'{stage}: git apply {flags}: {result.stderr}'
            actual = tree(Path(directory))
            assert actual == {p: b.replace(b'\r\n', b'\n') for p,b in expected[i].items()}, f'{stage}: replay does not produce next checkpoint'
        print(f'PASS {stage}: real unified patch applies and reproduces next checkpoint (LF-normalized)')
    for removed in ['Part1/patterns.csv', 'Part1/pattern_counts.csv', 'Part1/llm.csv', 'Part2/pattern_counts.csv', 'Part2/patterns_evolution.csv', 'Part2/llm.csv', 'Part3/llm/llm.csv', 'Part3/llm/pattern_crosslanguage.csv']:
        assert not (ROOT / removed).exists(), 'Repeated dataset reintroduced: ' + removed
    print('PASS data/ is the sole authoritative pattern, count, evolution, LLM and cross-language dataset location')
    metrics = json.loads((PART / 'metrics/ruby_ast_metrics.json').read_text())
    from measure_part2 import HEADER
    expected_rows = []
    for stage in STAGES:
        files = metrics[stage]
        source = tree(PART / 'checkpoints' / stage)
        app_paths = {p for p in source if p.startswith('app/') and p.endswith('.rb')}
        assert {f['path'] for f in files} == app_paths, f'{stage}: metrics source coverage differs'
        for f in files:
            assert f['sha256'] == hashlib.sha256(source[f['path']]).hexdigest(), f'{stage}/{f["path"]}: stale metric source'
            assert f['sloc'] == sum(bool(s.strip()) and not s.lstrip().startswith('#') for s in source[f['path']].decode().splitlines()), 'Metric SLOC differs'
            assert f['method_count'] == len(f['methods']) and f['sum_method_cc'] == sum(m['cc'] for m in f['methods']), 'Method aggregates differ'
            assert f['max_method_cc'] == max((m['cc'] for m in f['methods']), default=0), 'Max CC differs'
            expected_rows.append([stage, 'Part2/checkpoints/'+stage+'/'+f['path'], f['sha256'], f['sloc'], f['method_count'], f['sum_method_cc'], f['max_method_cc'], len(f['explicit_app_dependencies']), '; '.join(f['explicit_app_dependencies'])])
        total = [stage, 'TOTAL app/**/*.rb', '', sum(f['sloc'] for f in files), sum(f['method_count'] for f in files), sum(f['sum_method_cc'] for f in files), max(f['max_method_cc'] for f in files), sum(len(f['explicit_app_dependencies']) for f in files), 'sum of per-file distinct explicit references']
        expected_rows.append(total)
        report = (ROOT / 'A7_Report.tex').read_text()
        slides = (ROOT / 'A7_slide.tex').read_text()
        label = 'Original' if stage == 'original' else stage
        assert label + ' & ' + ' & '.join(str(v) for v in total[3:8]) + r'\\' in report, f'{stage}: report metric table differs'
        assert stage + ' & ' + ' & '.join(str(v) for v in [*total[3:6], total[7]]) + r'\\' in slides, f'{stage}: slide metric table differs'
    with (PART / 'metrics/before_after.csv').open(newline='', encoding='utf-8') as f:
        assert list(csv.reader(f)) == [HEADER] + [[str(v) for v in r] for r in expected_rows], 'Metric CSV differs from detailed source-backed evidence'
    print('PASS metric source coverage/hashes/SLOC, JSON/CSV aggregates, and report/slides tables agree')
    from summarize_part2 import records
    observations, summaries = records()
    for name, rows in [('pattern_observations.csv', observations), ('snapshot_summary.csv', summaries)]:
        with (PART / 'evidence' / name).open(newline='', encoding='utf-8') as f:
            actual = list(csv.DictReader(f))
        assert actual == [{k: str(v) for k,v in row.items()} for row in rows], name + ': differs from current source-review records'
    for stage, row in zip(STAGES, summaries):
        numbers = [row[k] for k in ['pattern_types','pattern_instances','concrete_participant_classes','unique_participant_symbols','rejected_observations','uncertain_observations']]
        label = 'Original' if stage == 'original' else stage
        assert label + ' & ' + ' & '.join(str(n) for n in numbers) + r'\\' in report, f'{stage}: report snapshot counts differ'
        slide_values = [f'{numbers[0]}/{numbers[1]}', *numbers[2:]]
        assert stage + ' & ' + ' & '.join(str(n) for n in slide_values) + r'\\' in slides, f'{stage}: slide snapshot counts differ'
    print('PASS participant/observation source records, counts, report and slide tables agree')


if __name__ == '__main__':
    verify()
