#!/usr/bin/env python3
"""Token-reduction benchmark runner.

Sends each prompt to the Anthropic API twice — baseline (no system prompt)
and treatment (Rocky's SKILL.md body as system prompt) — and records output
token counts side by side.

Usage:
    cp benchmarks/.env.example .env   # set ANTHROPIC_API_KEY
    pip install -r benchmarks/requirements.txt
    python benchmarks/run.py
    python benchmarks/run.py --model claude-haiku-4-5-20251001
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = REPO_ROOT / "skills" / "hail-mary-rocky" / "SKILL.md"
PROMPTS_PATH = REPO_ROOT / "benchmarks" / "prompts.json"
RESULTS_PATH = REPO_ROOT / "benchmarks" / "results.json"

DEFAULT_MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024


def strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[i + 1:]).lstrip()
    return text


def load_system_prompt() -> str:
    return strip_frontmatter(SKILL_PATH.read_text(encoding="utf-8"))


def load_prompts() -> list[dict]:
    data = json.loads(PROMPTS_PATH.read_text(encoding="utf-8"))
    return data["prompts"]


def measure(client: Anthropic, model: str, prompt: str, system: str | None) -> int:
    kwargs = {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system is not None:
        kwargs["system"] = system
    msg = client.messages.create(**kwargs)
    return msg.usage.output_tokens


def compute_summary(results: list[dict]) -> dict:
    if not results:
        return {"n": 0, "mean_reduction_pct": 0.0, "weighted_reduction_pct": 0.0,
                "total_baseline_tokens": 0, "total_rocky_tokens": 0}
    total_b = sum(r["baseline_tokens"] for r in results)
    total_r = sum(r["rocky_tokens"] for r in results)
    weighted = round((total_b - total_r) / total_b * 100, 1) if total_b else 0.0
    arithmetic = round(sum(r["reduction_pct"] for r in results) / len(results), 1)
    return {
        "n": len(results),
        "mean_reduction_pct": arithmetic,
        "weighted_reduction_pct": weighted,
        "total_baseline_tokens": total_b,
        "total_rocky_tokens": total_r,
    }


def main() -> int:
    load_dotenv(override=True)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set. Use .env or environment variable.",
              file=sys.stderr)
        return 1

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"Anthropic model id (default: {DEFAULT_MODEL})")
    parser.add_argument("--out", default=str(RESULTS_PATH),
                        help="output JSON path")
    args = parser.parse_args()

    client = Anthropic()
    system_prompt = load_system_prompt()
    prompts = load_prompts()
    timestamp = datetime.now(timezone.utc).isoformat()

    results: list[dict] = []
    for p in prompts:
        pid = p["id"]
        text = p["prompt"]
        print(f"[{pid}] baseline...", flush=True)
        baseline = measure(client, args.model, text, system=None)
        print(f"[{pid}] rocky...", flush=True)
        rocky = measure(client, args.model, text, system=system_prompt)
        reduction = round((baseline - rocky) / baseline * 100, 1) if baseline else 0.0
        sign = "-" if reduction >= 0 else "+"
        print(f"[{pid}] baseline={baseline} rocky={rocky} -> {sign}{abs(reduction)}%")
        results.append({
            "id": pid,
            "category": p.get("category"),
            "language": p.get("language"),
            "prompt": text,
            "baseline_tokens": baseline,
            "rocky_tokens": rocky,
            "reduction_pct": reduction,
            "model": args.model,
            "timestamp_utc": timestamp,
        })

    summary = compute_summary(results)
    out_path = Path(args.out)
    out_path.write_text(
        json.dumps({"results": results, "summary": summary}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"\nWrote {out_path} (mean reduction: -{summary['mean_reduction_pct']}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
