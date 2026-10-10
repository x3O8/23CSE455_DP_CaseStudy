"""Verify immutable source, final manifest/ZIP, and high-confidence secret patterns.

Run from any directory with Python 3: python A7/tools/check_submission.py.
Run after packaging with --zip path/to/A7_submission.zip.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".bundle", "node_modules", "__pycache__", ".git"}
RUNTIME_DIRS = {"log", "tmp", "storage", "coverage"}


def submission_files():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if any(part in RUNTIME_DIRS for part in rel.parts) and path.name != ".keep":
            continue
        if path.name == ".env" or (path.name.startswith(".env.") and path.name not in {".env.dist", ".env.example"}):
            continue
        if path.suffix in {".aux", ".log", ".toc", ".lof", ".lot", ".out", ".synctex"}:
            continue
        yield path


def check_baseline():
    record = json.loads((ROOT / "data/baseline_source_manifest.json").read_text())
    errors = []
    for rel, digest in record["files"].items():
        path = ROOT / "code" / rel
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            errors.append("Baseline file missing or changed: " + rel)
    if errors:
        raise ValueError("\n".join(errors))
    return f"PASS: {len(record['files'])} original upstream files match SHA-256 manifest."


def check_secrets(files):
    # Deliberately avoid reporting matching values. Retained upstream fixture
    # passwords and commented Devise examples are not deployed credentials.
    patterns = {
        "private key": rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
        "GitHub token": rb"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b",
        "AWS access key": rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
        "Stripe live key": rb"\b(?:sk|rk)_live_[A-Za-z0-9]{16,}\b",
        "Google API key": rb"\bAIza[A-Za-z0-9_-]{35}\b",
        "credential URL": rb"(?:postgres(?:ql)?|mysql|redis)://[^\s/:]+:[^\s/@]+@",
    }
    hits = []
    for path in files:
        content = path.read_bytes()
        # PDF text is scanned when pypdf is available, not compressed byte streams.
        if path.suffix == ".pdf":
            from pypdf import PdfReader
            content = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages).encode()
        for label, pattern in patterns.items():
            if re.search(pattern, content):
                hits.append(f"{path.relative_to(ROOT)}: {label}")
        if path.name in {"master.key", "credentials.key"} or path.suffix in {".pem", ".p12", ".pfx"}:
            hits.append(f"{path.relative_to(ROOT)}: key material filename")
    if hits:
        raise ValueError("Potential credentials (values suppressed):\n" + "\n".join(hits))
    return f"PASS: high-confidence secret scan across {len(files)} final files, including extracted PDF text.\nScope: private keys, GitHub tokens, AWS access keys, Stripe live keys, Google API keys, credential URLs, key filenames.\nReviewed exclusions: upstream synthetic test passwords; commented generated Devise secret/pepper examples; encrypted credentials.yml.enc without master.key. No live credentials were found. This pattern scan is not a guarantee against every possible secret format."


def check_zip(path, files):
    expected = {"A7/" + p.relative_to(ROOT).as_posix() for p in files}
    with zipfile.ZipFile(path) as archive:
        names = [info.filename for info in archive.infolist() if not info.is_dir()]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("ZIP members differ from final file manifest")
        for name in names:
            if archive.read(name) != (ROOT / name.removeprefix("A7/")).read_bytes():
                raise ValueError("ZIP content mismatch: " + name)
        if archive.testzip() is not None:
            raise ValueError("ZIP CRC check failed")
    return f"PASS: ZIP has one top-level A7/ folder; {len(expected)} files match final content; CRC check passed."


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", type=Path)
    args = parser.parse_args()
    from check_part2 import verify
    verify()
    files = list(submission_files())
    print(check_baseline())
    print(check_secrets(files))
    if args.zip:
        print(check_zip(args.zip, files))
