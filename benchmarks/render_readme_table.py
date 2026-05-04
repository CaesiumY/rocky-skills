#!/usr/bin/env python3
"""Render the benchmark results table into README markers.

Reads benchmarks/results.json and replaces the content between
<!-- benchmarks:start --> ... <!-- benchmarks:end --> markers in README.md and
README.ko.md with a generated markdown table.

Usage:
    python benchmarks/render_readme_table.py
    python benchmarks/render_readme_table.py --print
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_PATH = REPO_ROOT / "benchmarks" / "results.json"
README_EN = REPO_ROOT / "README.md"
README_KO = REPO_ROOT / "README.ko.md"

START = "<!-- benchmarks:start -->"
END = "<!-- benchmarks:end -->"

EN_HEADERS = ("Prompt", "Baseline", "Rocky", "Saved")
KO_HEADERS = ("프롬프트", "Baseline", "Rocky", "절감")

PENDING_EN = "_Benchmarks pending. Run `python benchmarks/run.py` to populate._"
PENDING_KO = "_벤치마크 결과 없음. `python benchmarks/run.py` 실행 후 갱신._"


def render_table(results: list[dict], summary: dict, headers: tuple, lang: str) -> str:
    if not results:
        return (PENDING_KO if lang == "ko" else PENDING_EN) + "\n"
    lines = [
        f"| {headers[0]} | {headers[1]} | {headers[2]} | {headers[3]} |",
        "|---|---:|---:|---:|",
    ]
    for r in results:
        sign = "-" if r["reduction_pct"] >= 0 else "+"
        lines.append(
            f"| `{r['id']}` | {r['baseline_tokens']} | {r['rocky_tokens']} | {sign}{abs(r['reduction_pct'])}% |"
        )
    mean = summary.get("mean_reduction_pct", 0.0)
    weighted = summary.get("weighted_reduction_pct", 0.0)
    n = summary.get("n", 0)
    model = results[0].get("model", "?")
    ts = results[0].get("timestamp_utc", "")
    date = ts[:10] if ts else "?"
    if lang == "en":
        footer = (
            f"\n**Mean reduction: −{mean}%** (token-weighted: −{weighted}%) "
            f"across {n} prompts on `{model}`.\n\n"
            f"_Measured against the Anthropic API on {date} — `usage.output_tokens` per response, no estimation._"
        )
    else:
        footer = (
            f"\n**평균 절감률: −{mean}%** (토큰 가중: −{weighted}%) — "
            f"{n}개 프롬프트, 모델 `{model}`.\n\n"
            f"_{date}에 Anthropic API로 직접 측정 — 응답의 `usage.output_tokens` 값, 추정 없음._"
        )
    return "\n".join(lines) + "\n" + footer + "\n"


def replace_block(text: str, replacement: str) -> tuple[str, bool]:
    pattern = re.compile(rf"({re.escape(START)})(.*?)({re.escape(END)})", re.DOTALL)
    if not pattern.search(text):
        return text, False
    new = pattern.sub(lambda m: f"{m.group(1)}\n{replacement}\n{m.group(3)}", text)
    return new, True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--print", action="store_true",
                        help="print rendered tables instead of editing READMEs")
    args = parser.parse_args()

    if not RESULTS_PATH.exists():
        print(f"ERROR: {RESULTS_PATH} not found. Run benchmarks/run.py first.",
              file=sys.stderr)
        return 1
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    results = data.get("results", [])
    summary = data.get("summary", {})

    en_table = render_table(results, summary, EN_HEADERS, "en")
    ko_table = render_table(results, summary, KO_HEADERS, "ko")

    if args.print:
        print("== README.md ==\n" + en_table)
        print("== README.ko.md ==\n" + ko_table)
        return 0

    for path, table in [(README_EN, en_table), (README_KO, ko_table)]:
        if not path.exists():
            print(f"skip: {path} (not found)")
            continue
        text = path.read_text(encoding="utf-8")
        new, ok = replace_block(text, table)
        if not ok:
            print(f"skip: {path} (no markers {START} ... {END})")
            continue
        path.write_text(new, encoding="utf-8")
        print(f"updated: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
