# Benchmarks — token reduction measurement

Measures how many output tokens Rocky's voice saves vs. an unstyled baseline, on a fixed set of prompts. Results feed the table in the top-level [README.md](../README.md) and [README.ko.md](../README.ko.md).

## Methodology

For each prompt in [`prompts.json`](./prompts.json):

1. **Baseline** — send to the Anthropic API with no system prompt.
2. **Treatment** — send the same prompt with [`skills/hail-mary-rocky/SKILL.md`](../skills/hail-mary-rocky/SKILL.md) (frontmatter stripped) loaded as the system prompt.

Both calls use identical `max_tokens` and `model`. Only `usage.output_tokens` from the API response is recorded — no local tokenizer is involved, so counts match billing.

`reduction_pct` per prompt = `(baseline - rocky) / baseline * 100`. The overall summary reports both an arithmetic mean across prompts and a token-weighted mean (more sensitive to long-prompt savings).

## Why this design

- **Real API token counts, not estimates.** Anthropic returns token usage in the response; using it removes any tokenizer-version skew.
- **No skill triggering, just system prompt injection.** This makes the measurement deterministic and runnable against any agent that supports system prompts. The skill's `description` (which controls Claude Code's auto-invocation) is irrelevant to compression and is excluded.
- **Same `max_tokens`, same model, same prompt.** Only the system prompt varies.
- **Results committed.** [`results.json`](./results.json) is checked in for reproducibility and so the README table can be rendered without rerunning the benchmark.

## Running

```bash
cp benchmarks/.env.example .env       # set ANTHROPIC_API_KEY
pip install -r benchmarks/requirements.txt
python benchmarks/run.py               # default: claude-sonnet-4-6
python benchmarks/render_readme_table.py
```

Override the model:

```bash
python benchmarks/run.py --model claude-haiku-4-5-20251001
```

## Cost

8 prompts × 2 calls × ~500 output tokens ≈ 8 000 output tokens per run. At Sonnet 4.6 rates this is well under $0.20. Haiku 4.5 is roughly an order of magnitude cheaper.

## Adding a prompt

Append an object to `prompts.json` with a unique `id`, a `category`, a `language` (`ko` or `en`), and the `prompt` text. Rerun `run.py` and `render_readme_table.py`.

Keep the prompt mix balanced — debugging, planning, support, how-to, and a low-compression "trivial" baseline (short Q&A where Rocky shouldn't shorten further). A skewed prompt set produces misleading averages.

## Relationship to `evals/`

- [`evals/evals.json`](../evals/evals.json) — **behavioral** evals: does the reply match Rocky's style rules? Designed for an LLM-as-judge harness.
- [`benchmarks/`](.) — **token** measurement: how many fewer output tokens does Rocky use?

The two are complementary. Behavioral correctness without token reduction means the style is gimmicky; token reduction without style fidelity means the skill regressed.
