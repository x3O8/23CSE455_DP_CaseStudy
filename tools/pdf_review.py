"""Render all deliverable pages and record hash-bound review metadata."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import subprocess
from datetime import datetime, timezone
from pypdf import PdfReader
from PIL import Image, ImageOps, ImageDraw

parser = argparse.ArgumentParser()
parser.add_argument('--pdftoppm', required=True)
args = parser.parse_args()
team = Path(__file__).resolve().parents[1]
evidence = team / 'test_result'
render_dir = evidence / 'pdf_pages'
render_dir.mkdir(parents=True, exist_ok=True)
manifest = {'generated_at': datetime.now(timezone.utc).isoformat(), 'files': []}
for name, prefix in [('A7_Final_Report.pdf', 'report'), ('A7_slide.pdf', 'slides')]:
    source = team / name
    reader = PdfReader(source)
    # Clear only this renderer's numbered pages and contact sheets.
    for old in render_dir.glob(f'{prefix}-*.png'):
        old.unlink()
    for old in render_dir.glob(f'{prefix}_contact_*.png'):
        old.unlink()
    subprocess.run([args.pdftoppm, '-r', '110', '-png', str(source), str(render_dir / prefix)], check=True)
    paths = sorted(render_dir.glob(f'{prefix}-*.png'))
    if len(paths) != len(reader.pages):
        raise RuntimeError(f'{name}: page/render mismatch')
    text = '\n\n'.join(f'--- PAGE {i+1} ---\n{page.extract_text()}' for i, page in enumerate(reader.pages))
    (evidence / f'pdf_{prefix}_text.txt').write_text(text, encoding='utf-8')
    for start in range(0, len(paths), 6):
        canvas = Image.new('RGB', (1600, 1650), 'white')
        draw = ImageDraw.Draw(canvas)
        for index, image_path in enumerate(paths[start:start+6]):
            tile = ImageOps.contain(Image.open(image_path).convert('RGB'), (760, 495))
            x, y = (index % 2) * 800, (index // 2) * 550
            canvas.paste(tile, (x+(800-tile.width)//2, y+35))
            draw.text((x+20, y+10), f'{prefix}: physical page {start+index+1}', fill='black')
        canvas.save(render_dir / f'{prefix}_contact_{start//6+1:02}.png')
    manifest['files'].append({'path': name, 'sha256': sha256(source.read_bytes()).hexdigest(),
        'pages': len(reader.pages), 'rendered_pages': [p.name for p in paths],
        'visual_review': 'PENDING: inspect every rendered page before recording completion'})
(evidence / 'pdf_review_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(json.dumps(manifest, indent=2))
