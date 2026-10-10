"""Check submission CSVs and source references without third-party dependencies.

Run from any directory: python A7/tools/check_csv.py
Exit status is nonzero if a CSV or report reference fails validation.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
PATTERN_HEADER = "source_version,pattern_name,pattern_type,instance_name,participant_roles,source_locations,intent_and_evidence".split(",")
EVOLUTION_HEADER = PATTERN_HEADER + ["status_after_change", "change_description"]
COUNT_HEADER = "source_version,summary,pattern_name,count".split(",")
LLM_HEADER = "part,model_and_date,prompt_file,input_file,output_file,evaluation,verification_file".split(",")
CROSS_HEADER = "pattern_name,instance_name,language,snippet_path,source_loc,max_function_cc,runtime_compiler,test_command,test_result,median_process_ms,language_notes".split(",")
STAGES = ["Baseline", "Architecture", "Pattern discovery", "Evolution", "Cross-language", "Final audit"]
VERSIONS = ["Original baseline 5e15551", "After Change1", "After Change2", "After Change3"]
CSV_LOG: list[str] = []
REPORT_LOG: list[str] = []
ERRORS: list[str] = []
SOURCE_HASHES: dict[str, str] = {}


def check(condition: bool, message: str, log=CSV_LOG) -> None:
    log.append(("PASS " if condition else "FAIL ") + message)
    if not condition:
        ERRORS.append(message)


def table(path: str, header: list[str]) -> list[dict[str, str]]:
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    check(bool(rows) and rows[0] == header, f"{path}: exact header")
    records = []
    for index, row in enumerate(rows[1:], 2):
        valid = len(row) == len(header) and any(cell.strip() for cell in row)
        check(valid, f"{path}:{index}: complete CSV record")
        if valid:
            records.append(dict(zip(header, row)))
    return records


def reference(value: str, context: str, log=CSV_LOG, allow_directory=False) -> None:
    value = value.strip()
    match = re.fullmatch(r"(.+?)(?::(\d+)(?:--?([0-9]+))?)?", value)
    if not match:
        check(False, f"{context}: malformed reference {value!r}", log)
        return
    rel, start, end = match.groups()
    target = (ROOT / rel).resolve()
    contained = target.is_relative_to(ROOT)
    exists = contained and (target.is_file() or (allow_directory and target.is_dir()))
    check(exists, f"{context}: {value} exists within submission", log)
    if exists and target.is_file() and rel.startswith(("code/", "Part2/code/", "Part3/")):
        SOURCE_HASHES[rel] = hashlib.sha256(target.read_bytes()).hexdigest()
    if start and exists:
        lines = len(target.read_text(encoding="utf-8", errors="replace").splitlines())
        first, last = int(start), int(end or start)
        check(1 <= first <= last <= lines, f"{context}: {value} range within {lines} lines", log)


def copies(paths: list[str], header: list[str]) -> list[dict[str, str]]:
    records = [table(path, header) for path in paths]
    for path, rows in zip(paths[1:], records[1:]):
        check(rows == records[0], f"{path}: rows equal {paths[0]}")
    return records[0]


def validate_csvs() -> None:
    for removed in ["Part1/patterns.csv", "Part1/pattern_counts.csv", "Part1/llm.csv", "Part2/patterns_evolution.csv", "Part2/pattern_counts.csv", "Part2/llm.csv", "Part3/llm/llm.csv", "Part3/llm/pattern_crosslanguage.csv"]:
        check(not (ROOT / removed).exists(), f"canonical datasets: removed mirror {removed} remains absent")
    patterns = table("data/patterns.csv", PATTERN_HEADER)
    evolution = table("data/patterns_evolution.csv", EVOLUTION_HEADER)
    counts = table("data/pattern_counts.csv", COUNT_HEADER)
    evolved_counts = counts
    llm = table("data/llm.csv", LLM_HEADER)
    cross = table("data/cross_language.csv", CROSS_HEADER)
    for part in ['template-method', 'strategy']:
        for language in ['java', 'python', 'javascript', 'cpp']:
            readme = ROOT / 'Part3' / part / language / 'README.md'
            text = readme.read_text(encoding='utf-8')
            check('data/cross_language.csv' in text and 'Part3/llm/pattern_crosslanguage.csv' not in text, f'{part}/{language}: README points to canonical measured commands')
    check(len(patterns) == 1 and patterns[0]["pattern_name"] == "Template Method", "baseline: exactly one Template Method instance")
    check(len(evolution) == 5, "evolution: five nonblank pattern records")
    for row in patterns + evolution:
        check(all(row.values()), f"pattern {row['source_version']}/{row['pattern_name']}: no blank fields")
        check(row["source_version"] in VERSIONS and row["pattern_type"] == "Behavioral", f"pattern {row['source_version']}: valid version/type")
        if row in evolution:
            stage = ["original", "Change1", "Change2", "Change3"][VERSIONS.index(row["source_version"])]
            expected_prefix = f"Part2/checkpoints/{stage}/"
        else:
            expected_prefix = "code/"
        for value in row["source_locations"].split(";"):
            check(value.strip().startswith(expected_prefix), f"{row['source_version']}: correct source snapshot prefix")
            check(bool(re.search(r":\d+-\d+$", value)), f"{row['source_version']}: explicit source line bounds")
            reference(value, row["source_version"])
    check([(r["source_version"], r["status_after_change"]) for r in evolution] == [(VERSIONS[0], "baseline"), (VERSIONS[1], "preserved"), (VERSIONS[2], "preserved"), (VERSIONS[3], "preserved"), (VERSIONS[3], "newly_introduced")], "evolution: valid ordered stages/statuses")
    check([row["part"] for row in llm] == STAGES + ["Part2 verification experiment 07"], "LLM: six retained stages and separate current experiment in order")
    for row in llm:
        check(all(row.values()), f"LLM {row['part']}: no blank fields")
        if row['part'] in STAGES:
            check(row["model_and_date"] == "unknown historical model/date", f"LLM {row['part']}: unknown historical metadata disclosed")
        else:
            check(row['model_and_date'] == 'GPT-6 (system-identified family; deployment alias unavailable); 2026-10-11 Asia/Calcutta', 'experiment 07: actual available model identity and local interaction date disclosed')
        for field in ["prompt_file", "input_file", "output_file", "verification_file"]:
            for value in row[field].split(";"):
                reference(value, f"LLM {row['part']}/{field}", allow_directory=True)
    recovery = [llm[i]["prompt_file"] for i in [1, 2]] if len(llm) >= 6 else []
    for path in recovery:
        check("VERBATIM-RECOVERY STATUS" in (ROOT / path).read_text(encoding="utf-8"), f"{path}: recovery note retained without invented transcript")
    prompt = (ROOT / 'llm-analysis/prompts/prompt-07-part2-verification.txt').read_text(encoding='utf-8')
    wrapper = (ROOT / 'Part2/Part2_prompt.txt').read_text(encoding='utf-8')
    check('RECOVERY NOTE' in wrapper and '\nBEGIN VERBATIM NEW PROMPT\n' + prompt + '\nEND VERBATIM NEW PROMPT\n' in wrapper, 'experiment 07: exact dispatched prompt retained separately from recovery note')
    metadata = json.loads((ROOT / 'llm-analysis/results/experiment-07-metadata.json').read_text(encoding='utf-8'))
    check(metadata['interaction_date'] == '2026-10-11' and metadata['timezone'] == 'Asia/Calcutta' and metadata['model_family'] == 'GPT-6', 'experiment 07: recorded current interaction metadata')
    check(metadata['deployment_alias'] is None and metadata['access_tier'] is None and metadata['fresh_test_execution'] is False, 'experiment 07: unavailable deployment/tier and no new model-run tests disclosed')
    for rel, digest in metadata['files'].items():
        reference(rel, 'experiment 07 artifact')
        check(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest, f'experiment 07: immutable recorded artifact hash {rel}')
    frozen = (ROOT / 'llm-analysis/prompts/input-07-part2-verification.md').read_text(encoding='utf-8')
    captured = json.loads((ROOT / 'llm-analysis/prompts/input-07-source-hashes.json').read_text(encoding='utf-8'))
    for rel, digest in captured.items():
        reference(rel, 'experiment 07 source')
        check('## ' + rel + ' (SHA-256 ' + digest + ')' in frozen, f'experiment 07: frozen source section {rel}')
        if rel != 'Part2/changes/Change1/diff.md':
            check(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest, f'experiment 07: captured executable source/receipt unchanged {rel}')
    evaluation = (ROOT / 'llm-analysis/results/evaluation-07.md').read_text(encoding='utf-8')
    check('human corrections' in evaluation and 'Student/faculty acceptance of the new response is pending.' in evaluation, 'experiment 07: actual prior user corrections distinguished from pending human acceptance')
    for version in VERSIONS:
        inventory = patterns if version == VERSIONS[0] else [r for r in evolution if r["source_version"] == version]
        counted = [r for r in counts if r["source_version"] == version]
        actual = Counter(r["pattern_name"] for r in inventory)
        declared = {r["pattern_name"]: int(r["count"]) for r in counted if r["summary"] == "per_pattern"}
        check(declared == dict(actual), f"{version}: per_pattern counts match inventory")
        totals = {r["summary"]: int(r["count"]) for r in counted if r["summary"] != "per_pattern"}
        check(totals == {"total_pattern_types": len(actual), "total_pattern_instances": sum(actual.values())}, f"{version}: totals match inventory")
    strategy_versions = [r["source_version"] for r in evolution if r["pattern_name"] == "Strategy"]
    check(strategy_versions == ["After Change3"], "Strategy first and only appears after Change3")
    check(len(cross) == 8, "cross-language: eight snippets")
    check({(r["pattern_name"], r["language"]) for r in cross} == {(p, language) for p in ["Template Method", "Strategy"] for language in ["java", "python", "javascript", "cpp"]}, "cross-language: complete two-pattern/four-language matrix")
    for row in cross:
        reference(row["snippet_path"], f"cross-language {row['pattern_name']}/{row['language']}")
        check(all(row.values()) and int(row["source_loc"]) > 0 and int(row["max_function_cc"]) > 0 and float(row["median_process_ms"]) > 0, f"cross-language {row['language']}: populated positive metrics")
        snippet = ROOT / row["snippet_path"]
        if snippet.is_file():
            source = snippet.read_text(encoding="utf-8")
            # These eight compact snippets have no block comments or inline
            # comments. C++ #include directives count as source, Python #
            # comment-only lines do not. Keep this rule language-aware.
            comment_prefixes = ("#",) if row["language"] == "python" else ("//",)
            sloc = sum(bool(line.strip()) and not line.lstrip().startswith(comment_prefixes) for line in source.splitlines())
            check(int(row["source_loc"]) == sloc, f"cross-language {row['pattern_name']}/{row['language']}: LOC matches {sloc} nonblank/noncomment source lines")
            if row["language"] == "cpp":
                main = re.search(r"int\s+main\s*\([^)]*\)\s*\{(.*)\}\s*$", source, re.S)
                # The only decision in either current C++ snippet is its
                # main function's for loop; include main in function CC.
                cc = 1 + len(re.findall(r"\b(?:if|for|while|case|catch)\b|&&|\|\||\?", main.group(1))) if main else 0
                check(int(row["max_function_cc"]) == cc, f"cross-language {row['pattern_name']}/cpp: main CC matches {cc}")
        evidence = ROOT / f"Part3/evidence/{'template-method' if row['pattern_name'] == 'Template Method' else 'strategy'}_{row['language']}.txt"
        if evidence.is_file():
            measured_text = evidence.read_text(encoding="utf-8")
            recorded = re.search(r"median_process_ms:\s*([0-9.]+)", measured_text)
            check(bool(recorded) and float(recorded.group(1)) == float(row["median_process_ms"]), f"cross-language {row['pattern_name']}/{row['language']}: median equals retained timing evidence")
            samples = re.search(r"measured_ms:\s*([^\n]+)", measured_text)
            values = [float(value.strip()) for value in samples.group(1).split(",")] if samples else []
            check(len(values) == 5 and median(values) == float(row["median_process_ms"]), f"cross-language {row['pattern_name']}/{row['language']}: median equals five measured samples")
        else:
            check(False, f"cross-language {row['pattern_name']}/{row['language']}: retained timing evidence exists")


def validate_report() -> None:
    path = ROOT / "A7_Report.tex"
    report = path.read_text(encoding="utf-8")
    # Decode the escapes used by \code and \texttt; scan all source-root paths,
    # including plain text and listings, so path citations outside \code count.
    decoded = report.replace(r"\_", "_").replace(r"\-", "-")
    pattern = re.compile(r"(?<![A-Za-z0-9_/.])(?:Part2/code|code|app|config|db|spec|Part3|data|llm-analysis|Part1|Part2|tools|test_result)/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]*(?::\d+(?:--?\d+)?)?")
    found = list(pattern.finditer(decoded))
    check(bool(found), "report: source/artifact path references extracted", REPORT_LOG)
    unique = set()
    for match in found:
        value = match.group().rstrip(".")
        if value in unique:
            continue
        unique.add(value)
        line = decoded[:match.start()].count("\n") + 1
        check(not value.startswith(("app/", "config/", "db/", "spec/")), f"report:{line}: {value} identifies baseline/evolved snapshot", REPORT_LOG)
        reference(value, f"report:{line}", REPORT_LOG, allow_directory=True)
    # Explicitly inspect every listing input, even if its filename does not
    # begin with a recognized source root. This also checks optional bounds.
    listings = list(re.finditer(r"\\lstinputlisting\s*(?:\[([^]]*)\]\s*)?\{([^}]*)\}", decoded, re.S))
    for listing in listings:
        options, value = listing.groups()
        value = value.strip()
        line = decoded[:listing.start()].count("\n") + 1
        check(value.startswith(("code/", "Part2/code/", "Part2/checkpoints/", "Part3/")), f"report:{line}: listing {value} identifies source snapshot", REPORT_LOG)
        reference(value, f"report:{line}/listing", REPORT_LOG)
        bounds = dict(re.findall(r"\b(firstline|lastline)\s*=\s*(\d+)", options or ""))
        if bounds:
            target = ROOT / value
            last = bounds.get("lastline", str(len(target.read_text(encoding="utf-8").splitlines()))) if target.is_file() else "0"
            reference(f"{value}:{bounds.get('firstline', '1')}-{last}", f"report:{line}/listing bounds", REPORT_LOG)
    REPORT_LOG.append(f"INFO {len(listings)} explicit source listing inputs checked")
    REPORT_LOG.append(f"INFO {len(found)} occurrences; {len(unique)} distinct path references checked")
    REPORT_LOG.append(f"INFO Report SHA256 {hashlib.sha256(path.read_bytes()).hexdigest()}")


def main() -> int:
    validate_csvs()
    validate_report()
    evidence = ROOT / "test_result"
    evidence.mkdir(exist_ok=True)
    csv_failures = sum(line.startswith("FAIL ") for line in CSV_LOG)
    report_failures = sum(line.startswith("FAIL ") for line in REPORT_LOG)
    CSV_LOG.insert(0, f"CSV consistency: {'PASS' if not csv_failures else 'FAIL'} ({csv_failures} failures)")
    REPORT_LOG.insert(0, f"Report source paths: {'PASS' if not report_failures else 'FAIL'} ({report_failures} failures)")
    for path in sorted(ROOT.rglob("*.csv")):
        CSV_LOG.append(f"INFO CSV SHA256 {path.relative_to(ROOT).as_posix()} {hashlib.sha256(path.read_bytes()).hexdigest()}")
    for path, digest in sorted(SOURCE_HASHES.items()):
        REPORT_LOG.append(f"INFO Source SHA256 {path} {digest}")
    (evidence / "csv_consistency.txt").write_text("\n".join(CSV_LOG) + "\n", encoding="utf-8")
    (evidence / "report_source_paths.txt").write_text("\n".join(REPORT_LOG) + "\n", encoding="utf-8")
    print(CSV_LOG[0])
    print(REPORT_LOG[0])
    for error in ERRORS:
        print("FAIL", error)
    return bool(ERRORS)


if __name__ == "__main__":
    raise SystemExit(main())
