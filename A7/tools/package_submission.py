"""Regenerate FINAL_TREE.txt, audit final files, and ZIP one A7/ team folder."""
from pathlib import Path
import hashlib
import zipfile
import argparse
from check_submission import ROOT, submission_files, check_baseline, check_secrets, check_zip


def write_zip(destination, files):
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive.write(path, "A7/" + path.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT.parent / 'A7_submission.zip')
    args = parser.parse_args()
    from check_part2 import verify
    verify()
    evidence = ROOT / "test_result"
    evidence.mkdir(exist_ok=True)
    receipts = [evidence / name for name in ["baseline_source_validation.txt", "secret_scan.txt", "package_verification.txt"]]
    for path in receipts:
        if not path.exists():
            path.write_text("Verification pending.\n", encoding="utf-8")
    tree = ROOT / "FINAL_TREE.txt"
    tree.touch(exist_ok=True)
    files = list(submission_files())
    directories = sorted({p.parent.relative_to(ROOT).as_posix() for p in files})
    tree.write_text("A7/\n" + "\n".join("  " + p.relative_to(ROOT).as_posix() for p in files) + f"\n\n{len(files)} packaged files. Generated from final source and evidence; runtime caches and installed dependencies excluded.\n", encoding="utf-8")
    baseline = check_baseline()
    secrets = check_secrets(files)
    receipts[0].write_text(baseline + "\n", encoding="utf-8")
    receipts[1].write_text(secrets + "\n", encoding="utf-8")
    destination = args.output.resolve()
    write_zip(destination, files)
    first_result = check_zip(destination, files)
    receipts[2].write_text(first_result + "\n", encoding="utf-8")
    # Repack the verified receipt, then compare every final member byte again.
    write_zip(destination, files)
    final_result = check_zip(destination, files)
    if final_result != first_result:
        raise ValueError("Final archive verification changed")
    if check_secrets(files) != secrets:
        raise ValueError("Secret-scan scope changed")
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    proof = "\n".join([baseline, secrets, final_result, "ZIP SHA-256: " + digest]) + "\n"
    destination.with_suffix('.validation.txt').write_text(proof, encoding="utf-8")
    print(proof)
    print("Created: " + str(destination))
