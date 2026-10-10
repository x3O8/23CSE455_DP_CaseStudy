"""Reconstruct pedagogical checkpoints from retained source, without inventing history.

Run python A7/tools/rebuild_part2.py. No Git mutation or Rails runtime required.
Only known generated checkpoint files are removed. See Part2/README.md for provenance.
"""
from pathlib import Path
import csv
import difflib
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
PART = ROOT / 'Part2'
STAGES = ['original', 'Change1', 'Change2', 'Change3']
VERSIONS = ['Original baseline 5e15551', 'After Change1', 'After Change2', 'After Change3']
EXCLUDED = {'log', 'tmp', 'storage', '.bundle', '.git', '__pycache__', 'coverage', 'node_modules'}


def tree(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob('*'))
            if p.is_file() and (p.name == '.keep' or not any(x in EXCLUDED for x in p.relative_to(root).parts))
            and not (p.name == '.env' or p.name == 'master.key')}


def replace(data, path, old, new):
    text = data[path].decode().replace('\r\n', '\n')
    assert old in text, f'Expected source fragment missing in {path}: {old!r}'
    data[path] = text.replace(old, new).encode()


def checkpoints():
    original, final = tree(ROOT / 'code'), tree(PART / 'code')
    c2 = dict(final)
    for path in list(c2):
        if ('cancellation' in path or path == 'spec/requests/booking_cancellations_spec.rb'):
            del c2[path]
    c2['app/controllers/bookings_controller.rb'] = original['app/controllers/bookings_controller.rb']
    c2['.env.dist'] = original['.env.dist']
    replace(c2, 'db/schema.rb', '2026_10_10_190000', '2026_10_04_171000')
    replace(c2, 'db/schema.rb', '    t.decimal "cancellation_refund_amount", precision: 10, scale: 2\n', '')
    c1 = dict(c2)
    for path in ['app/services/room_upgrade.rb', 'db/migrate/20261004171000_add_room_upgrade_fields_to_bookings.rb', 'spec/services/room_upgrade_spec.rb']:
        del c1[path]
    c1['app/models/room.rb'] = original['app/models/room.rb']
    replace(c1, 'app/models/booking.rb', '  belongs_to :upgraded_from_room, class_name: "Room", optional: true\n', '')
    replace(c1, 'app/models/booking.rb', '  scope :active, -> { where(canceled_at: nil) }\n\n', '')
    replace(c1, 'app/models/booking.rb', ' || canceled?', '')
    replace(c1, 'app/models/booking.rb', 'room.bookings.active.where.not', 'room.bookings.where.not')
    replace(c1, 'db/schema.rb', '2026_10_04_171000', '2026_10_04_170000')
    replace(c1, 'db/schema.rb', '    t.bigint "upgraded_from_room_id"\n', '')
    replace(c1, 'db/schema.rb', '    t.index ["upgraded_from_room_id"], name: "index_bookings_on_upgraded_from_room_id"\n', '')
    replace(c1, 'db/schema.rb', '  add_foreign_key "bookings", "rooms", column: "upgraded_from_room_id"\n', '')
    return [original, c1, c2, final]


def unified(before, after):
    out = []
    for path in sorted(before.keys() | after.keys()):
        if before.get(path) == after.get(path):
            continue
        a, b = before.get(path, b''), after.get(path, b'')
        # All changes in these checkpoints are text. Refuse unsupported binary changes.
        aa, bb = a.decode('utf-8').splitlines(True), b.decode('utf-8').splitlines(True)
        aa = [s.replace('\r\n', '\n') for s in aa]
        bb = [s.replace('\r\n', '\n') for s in bb]
        out.append('diff --git a/' + path + ' b/' + path + '\n')
        if path not in before:
            out.append('new file mode 100644\n')
        elif path not in after:
            out.append('deleted file mode 100644\n')
        out.extend(difflib.unified_diff(aa, bb, fromfile='a/'+path if path in before else '/dev/null',
                                        tofile='b/'+path if path in after else '/dev/null', n=3))
    return ''.join(out)


def write_csv(path, header, rows):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def build():
    sources = checkpoints()
    manifest = {'basis': 'Retained A7/code baseline and A7/Part2/code final source; intermediate stages reconstructed, not historical commits.', 'stages': {}}
    for stage, files in zip(STAGES, sources):
        dest = PART / 'checkpoints' / stage
        dest.mkdir(parents=True, exist_ok=True)
        for old in tree(dest):
            if old not in files:
                (dest / old).unlink()
        for path, content in files.items():
            target = dest / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        manifest['stages'][stage] = {k: hashlib.sha256(v).hexdigest() for k, v in files.items()}
    (PART / 'checkpoint_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    for i, stage in enumerate(STAGES[1:], 1):
        (PART / 'changes' / stage / 'diff.patch').write_text(unified(sources[i-1], sources[i]), encoding='utf-8', newline='\n')
    evolution_path = ROOT / 'data/patterns_evolution.csv'
    with evolution_path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        header, rows = reader.fieldnames, list(reader)
    for row in rows:
        index = VERSIONS.index(row['source_version'])
        prefix = f'Part2/checkpoints/{STAGES[index]}/'
        refs = []
        for ref in row['source_locations'].split(';'):
            path, bounds = ref.strip().rsplit(':', 1)
            path = path.split('code/', 1)[1] if 'code/' in path else path.split(f'checkpoints/{STAGES[index]}/', 1)[1]
            n = len(sources[index][path].decode().splitlines())
            start, end = map(int, bounds.split('-'))
            assert 1 <= start <= end <= n, f'Invalid source bounds: {ref}'
            refs.append(f'{prefix}{path}:{start}-{end}')
        row['source_locations'] = '; '.join(refs)
    for path in [evolution_path]:
        write_csv(path, header, rows)
    counts = []
    for i, version in enumerate(VERSIONS):
        names = ['Template Method'] + (['Strategy'] if i == 3 else [])
        counts.extend(dict(source_version=version, summary='per_pattern', pattern_name=n, count=1) for n in names)
        counts.extend(dict(source_version=version, summary=s, pattern_name='', count=len(names)) for s in ['total_pattern_types', 'total_pattern_instances'])
    for path in [ROOT / 'data/pattern_counts.csv']:
        write_csv(path, ['source_version', 'summary', 'pattern_name', 'count'], counts)
    print('Rebuilt four checkpoint trees, SHA-256 manifest, three unified patches and canonical CSVs.')


if __name__ == '__main__':
    build()
