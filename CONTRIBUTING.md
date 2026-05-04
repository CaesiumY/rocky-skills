# Contributing

Thanks for taking a look. This file covers the parts of the repo that are easy to break if you don't know they exist.

## Repository layout

```
rocky-skills/
├── README.md, README.ko.md       # user-facing docs
├── AGENTS.md, GEMINI.md          # generic / Gemini CLI adapters
├── .cursor/rules/rocky.md        # Cursor adapter (MDC frontmatter)
├── .windsurf/rules/rocky.md      # Windsurf adapter
├── .clinerules                   # Cline adapter (single file)
├── install.sh, install.ps1       # one-line installers
├── skills/hail-mary-rocky/
│   ├── SKILL.md                  # ★ source of truth ★
│   ├── references/               # full style guide + worked examples
│   └── assets/                   # spinner-verbs + spinner install guide
├── benchmarks/                   # token-reduction measurement
│   ├── prompts.json              # input set
│   ├── run.py                    # API runner
│   ├── render_readme_table.py    # README table renderer
│   ├── results.json              # measured data (committed)
│   └── README.md                 # methodology
└── evals/                        # behavioral evals (style fidelity)
```

## Source of truth: `skills/hail-mary-rocky/SKILL.md`

The skill file is the only place the rules live in their full, authoritative form. The five adapter files (`AGENTS.md`, `GEMINI.md`, `.cursor/rules/rocky.md`, `.windsurf/rules/rocky.md`, `.clinerules`) are condensed copies — they exist because Cursor / Cline / Codex / Gemini / Windsurf don't read Claude Code skills.

### When you change `SKILL.md`

If your change touches anything in the **Compression rules**, **Korean rendering**, **Boundaries**, **Hard don'ts**, **Trigger phrases**, or **Priority order** sections of `SKILL.md`, you must update all five adapters. Keep the wording aligned.

The adapters intentionally repeat the rules verbatim so they're useful in isolation. Don't try to deduplicate by linking to SKILL.md only — agents reading the adapter often can't follow that link mid-conversation.

Quick check: `git diff -- skills/hail-mary-rocky/SKILL.md AGENTS.md GEMINI.md .cursor/rules/rocky.md .windsurf/rules/rocky.md .clinerules`. The diffs should move together.

### When you change only `references/` or `assets/`

Adapters don't need to be touched. References and assets are linked from SKILL.md and the adapters, but they aren't replicated.

## Adding a new adapter

When a new agent shows up:

1. Identify the agent's expected file path and frontmatter format. Check the agent's docs — formats change.
2. Copy `AGENTS.md` as a starting point. Adjust frontmatter and link paths.
3. Add a row to the **Multi-agent support** table in both `README.md` and `README.ko.md`.
4. Update the agent count badge in both READMEs.
5. Mention the new adapter in `install.sh` / `install.ps1`'s closing instructions block.
6. Update the layout tree in `README.md` and `README.ko.md` if the path is novel.

## Benchmarks — running and refreshing

Benchmarks measure output-token reduction by sending each prompt twice (baseline / Rocky) and comparing `usage.output_tokens` from the API response. Real billing tokens, no local tokenizer.

```bash
cp benchmarks/.env.example .env       # set ANTHROPIC_API_KEY
pip install -r benchmarks/requirements.txt
python benchmarks/run.py               # writes benchmarks/results.json
python benchmarks/render_readme_table.py
```

A run costs well under $0.20 on Sonnet 4.6. See [`benchmarks/README.md`](./benchmarks/README.md) for cost details.

Commit `benchmarks/results.json` together with the README changes — it's the data the rendered table reads from.

### Adding a benchmark prompt

Append an object to `benchmarks/prompts.json` with a unique `id`, a `category` (`debugging` / `planning` / `support` / `how-to` / `trivial`), a `language` (`ko` / `en`), and the `prompt` text. Rerun `run.py` and `render_readme_table.py`.

Keep the prompt mix balanced — debugging, planning, support, how-to, and at least one low-compression "trivial" baseline (short Q&A where Rocky shouldn't shorten further). A skewed prompt set produces misleading averages.

### `evals/` vs `benchmarks/`

| | `evals/` | `benchmarks/` |
|---|---|---|
| Question | Does Rocky reply match the style rules? | How many fewer output tokens does Rocky use? |
| Method | LLM-as-judge over expected behaviors | Real API token counts, baseline vs treatment |
| Output | Pass/fail per case | `reduction_pct` per prompt + summary |

Behavioral correctness without token reduction = the style is gimmicky. Token reduction without style fidelity = the skill regressed. Both signals matter.

## Updating Rocky's voice

The voice is *inspired by* Rocky from Andy Weir's *Project Hail Mary*. Don't paste verbatim quotes from the novel — the project is style-inspired, not canon-derivative.

Hard don'ts (also enforced in `SKILL.md`):

- Parody caveman / 우가우가 / baby talk
- Verbatim canon quotes
- Corporate voice ("기꺼이 도와드리겠습니다")
- Emoji spam, long warm-ups

If you want to debate a rule, open a PR with the proposed change to `SKILL.md` and the rationale in [`references/full-style-guide.md`](./skills/hail-mary-rocky/references/full-style-guide.md). Adapter updates and a benchmark refresh follow.

## License

By contributing you agree your contribution is licensed under [MIT](./LICENSE).
