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
import time
from datetime import datetime, timezone
from pathlib import Path

from anthropic import (
    Anthropic,
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    RateLimitError,
)
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = REPO_ROOT / "skills" / "hail-mary-rocky" / "SKILL.md"
PROMPTS_PATH = REPO_ROOT / "benchmarks" / "prompts.json"
RESULTS_PATH = REPO_ROOT / "benchmarks" / "results.json"

DEFAULT_MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024
MAX_ATTEMPTS = 3
BACKOFF_BASE_SECONDS = 2.0
RETRYABLE_EXCEPTIONS = (APIConnectionError, APITimeoutError, RateLimitError)


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


def measure(client: Anthropic, model: str, prompt: str, system: str | None) -> tuple[int, str]:
    """Send one prompt to the API and return (output_tokens, stop_reason).

    Retries on connection / timeout / rate-limit / 5xx with exponential backoff.
    4xx errors propagate immediately — they're permanent (bad model id, auth, etc.).
    Caller should check stop_reason: anything other than "end_turn" / "stop_sequence"
    means the response was cut off, and the token count is not directly comparable
    to a complete response.
    """
    kwargs = {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system is not None:
        kwargs["system"] = system
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            msg = client.messages.create(**kwargs)
            return msg.usage.output_tokens, (msg.stop_reason or "")
        except RETRYABLE_EXCEPTIONS as exc:
            if attempt == MAX_ATTEMPTS:
                raise
            wait = BACKOFF_BASE_SECONDS ** attempt
            print(f"  attempt {attempt}/{MAX_ATTEMPTS} failed ({type(exc).__name__}); retrying in {wait:.1f}s",
                  flush=True)
            time.sleep(wait)
        except APIStatusError as exc:
            if exc.status_code >= 500 and attempt < MAX_ATTEMPTS:
                wait = BACKOFF_BASE_SECONDS ** attempt
                print(f"  attempt {attempt}/{MAX_ATTEMPTS} failed (HTTP {exc.status_code}); retrying in {wait:.1f}s",
                      flush=True)
                time.sleep(wait)
                continue
            raise
    raise RuntimeError("unreachable: retry loop exited without returning")  # pragma: no cover


def write_results(out_path: Path, results: list[dict]) -> dict:
    summary = compute_summary(results)
    out_path.write_text(
        json.dumps({"results": results, "summary": summary}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return summary


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
    out_path = Path(args.out)
    try:
        for p in prompts:
            pid = p["id"]
            text = p["prompt"]
            print(f"[{pid}] baseline...", flush=True)
            baseline, baseline_stop = measure(client, args.model, text, system=None)
            print(f"[{pid}] rocky...", flush=True)
            rocky, rocky_stop = measure(client, args.model, text, system=system_prompt)
            baseline_truncated = baseline_stop not in ("end_turn", "stop_sequence")
            rocky_truncated = rocky_stop not in ("end_turn", "stop_sequence")
            reduction = round((baseline - rocky) / baseline * 100, 1) if baseline else 0.0
            sign = "-" if reduction >= 0 else "+"
            note = ""
            if baseline_truncated or rocky_truncated:
                note = (f"  WARN: response cut off "
                        f"(baseline_stop={baseline_stop!r}, rocky_stop={rocky_stop!r}); "
                        f"reduction% understates the real saving for this prompt")
                print(note, flush=True)
            print(f"[{pid}] baseline={baseline} rocky={rocky} -> {sign}{abs(reduction)}%")
            results.append({
                "id": pid,
                "category": p.get("category"),
                "language": p.get("language"),
                "prompt": text,
                "baseline_tokens": baseline,
                "rocky_tokens": rocky,
                "reduction_pct": reduction,
                "baseline_stop_reason": baseline_stop,
                "rocky_stop_reason": rocky_stop,
                "baseline_truncated": baseline_truncated,
                "rocky_truncated": rocky_truncated,
                "model": args.model,
                "timestamp_utc": timestamp,
            })
            write_results(out_path, results)
    except (APIConnectionError, APITimeoutError, RateLimitError, APIStatusError) as exc:
        n_done = len(results)
        n_total = len(prompts)
        print(f"\nERROR: API call failed after retries ({type(exc).__name__}): {exc}",
              file=sys.stderr)
        if n_done:
            print(f"Partial results saved: {n_done}/{n_total} prompts -> {out_path}",
                  file=sys.stderr)
        return 1

    summary = compute_summary(results)
    print(f"\nWrote {out_path} (mean reduction: -{summary['mean_reduction_pct']}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
