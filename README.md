# rocky-skills

> Cut your LLM output token bill by ~30–60% by replying in Rocky's compressed voice.
> Verdict-first, fragments, no filler, technical substance intact.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/agents-6-blue)](#multi-agent-support)
[![Korean README](https://img.shields.io/badge/한국어-README.ko.md-informational)](./README.ko.md)

Rocky is the alien engineer from Andy Weir's *Project Hail Mary*. His translation-layer voice — short fragments, verdict first, no filler, technical substance intact — happens to be a near-optimal output-compression algorithm for LLM agents. This repo packages that voice as a Claude Code skill plus drop-in adapters for Cursor, Codex, Gemini CLI, Windsurf, and Cline.

Korean README: [README.ko.md](./README.ko.md)

---

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/CaesiumY/rocky-skills/main/install.sh | bash
```

PowerShell (Windows):

```powershell
irm https://raw.githubusercontent.com/CaesiumY/rocky-skills/main/install.ps1 | iex
```

Claude Code only, via the skills CLI:

```bash
npx skills add CaesiumY/rocky-skills
```

Per-agent adapter copy: see [Multi-agent support](#multi-agent-support) below.

---

## Why output tokens?

Across Claude's current model lineup, **output tokens cost ~5× more than input tokens** — Sonnet 4.6 is $3/M in vs $15/M out, Haiku 4.5 is $1/M vs $5/M, Opus 4.7 is $5/M vs $25/M. The ratio is the same everywhere. A reply that's twice as long isn't twice as expensive — the longer half dominates the bill.

That's why this project is scoped deliberately to **output** compression. It doesn't touch your prompts, system messages, or tool descriptions (the input side — where, for example, [caveman](https://github.com/juliusbrussee/caveman)'s MCP middleware operates). Rocky just makes Claude reply in fewer tokens for the same answer, where each token saved is worth ~5× an input-side token saved.

If your bills tilt toward long replies, agentic loops, or chat-heavy workflows, that's the highest-leverage place to cut.

---

## Before / after

Same prompt — *"Why does my React component keep re-rendering?"* — same model.

**Without Rocky** (~140 output tokens):

> The reason your component is likely re-rendering on every parent update is that you are creating a new object reference on every render cycle. When you pass an inline object as a prop, React treats it as a new value each time the parent re-renders, which causes the child component to re-render as well. To fix this, you can either wrap the object in a `useMemo` hook so that the same reference is reused across renders, or you can move the object out of the component entirely so that it is defined once at module scope.

**With Rocky** (~52 output tokens):

> 매 렌더마다 새 객체 ref 생성. 인라인 객체 prop = 새 ref = 리렌더. `useMemo`로 감쌈. 아니면 컴포넌트 밖 상수로 뺌. React DevTools Profiler로 재렌더 원인 확인.

Same diagnosis. Same fix. ~63% fewer output tokens.

---

## Benchmarks

Output tokens compared on a fixed prompt set against a no-system-prompt baseline — **measured by real calls to the Anthropic API** (`usage.output_tokens` from each response, not a local tokenizer estimate, not synthetic data). Raw measurements are committed to [`benchmarks/results.json`](./benchmarks/results.json). Methodology: [`benchmarks/README.md`](./benchmarks/README.md). Numbers below are rendered automatically by `python benchmarks/render_readme_table.py`.

<!-- benchmarks:start -->
| Prompt | Baseline | Rocky | Saved |
|---|---:|---:|---:|
| `react-rerender` | 1024 | 347 | -66.1% |
| `support-overworked` | 87 | 37 | -57.5% |
| `arch-monolith-coupling` | 1024 | 447 | -56.3% |
| `sql-query-optimization` | 1024 | 426 | -58.4% |
| `git-rebase-conflict` | 586 | 363 | -38.1% |
| `ts-type-narrowing` | 1024 | 283 | -72.4% |
| `short-yes-no` | 77 | 46 | -40.3% |
| `python-listcomp-vs-generator` | 769 | 421 | -45.3% |

**Mean reduction: −54.3%** (token-weighted: −57.8%) across 8 prompts on `claude-sonnet-4-6`.

_Measured against the Anthropic API on 2026-05-04 — `usage.output_tokens` per response, no estimation._

<!-- benchmarks:end -->

To run the benchmark yourself:

```bash
cp benchmarks/.env.example .env       # set ANTHROPIC_API_KEY
pip install -r benchmarks/requirements.txt
python benchmarks/run.py
python benchmarks/render_readme_table.py
```

---

## Activation

**Always-on by default for all 6 supported agents.** Drop the adapter file into a project (or run the installer) and every reply uses Rocky's voice — no per-session trigger needed. Boundaries (code blocks, commits, legal text) are still respected; the rules in `SKILL.md` handle that automatically.

| Agent | Default state after install |
|---|---|
| Claude Code | always-on (rules merged into `CLAUDE.md` by `install.sh` / `install.ps1`) |
| Cursor | always-on (`alwaysApply: true` in `.cursor/rules/rocky.md`) |
| Windsurf | always-on (`trigger: always_on`) |
| Cline | always-on (`.clinerules` auto-loaded) |
| Codex / generic | always-on (`AGENTS.md` auto-loaded) |
| Gemini CLI | always-on (`GEMINI.md` auto-loaded) |

### Switching off and back on

The off-switch is for one-off tasks where the voice would be inappropriate (long docs, formal email):

- Disable for the current session: `normal mode` / `일반 모드` / `rocky off` / `stop caveman`
- Reactivate: `rocky` / `로키` / `rocky mode` / `caveman mode` / `헤일메리`

Next session restarts with the voice on.

### Skipping the CLAUDE.md merge (Claude Code only)

If you'd rather keep the Claude Code skill purely trigger-based (auto-invoked only when the skill description matches your prompt), pass `--skip-claude-md` to the installer:

```bash
curl -fsSL https://raw.githubusercontent.com/CaesiumY/rocky-skills/main/install.sh | bash -s -- --skip-claude-md
# PowerShell
iex "& { $(irm https://raw.githubusercontent.com/CaesiumY/rocky-skills/main/install.ps1) } -SkipClaudeMd"
```

The installer manages a marker-bounded block (`<!-- rocky-skills:start --> ... <!-- rocky-skills:end -->`) inside `CLAUDE.md`. Re-running install replaces the block in place, never duplicates it. Remove the block manually to revert.

---

## Multi-agent support

Rocky's rules live in [`skills/hail-mary-rocky/SKILL.md`](./skills/hail-mary-rocky/SKILL.md). Each agent gets a thin adapter that condenses those rules into the format the agent expects.

| Agent | Adapter file |
|---|---|
| Claude Code | [`skills/hail-mary-rocky/`](./skills/hail-mary-rocky/) |
| Codex / generic | [`AGENTS.md`](./AGENTS.md) |
| Cursor | [`.cursor/rules/rocky.md`](./.cursor/rules/rocky.md) |
| Gemini CLI | [`GEMINI.md`](./GEMINI.md) |
| Windsurf | [`.windsurf/rules/rocky.md`](./.windsurf/rules/rocky.md) |
| Cline | [`.clinerules`](./.clinerules) |

Adapters are condensed copies, not the source of truth. When [`SKILL.md`](./skills/hail-mary-rocky/SKILL.md) changes, see [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the propagation steps.

---

## How it works — Rocky's rules as a compression algorithm

Rocky's translation-layer style maps almost one-to-one onto LLM output compression. Each rule cuts tokens for a specific reason:

| Rule | Why it saves tokens |
|---|---|
| **Verdict first** | Frontloads the answer; readers don't need long ramps that the model would otherwise generate. |
| **Short sentences, fragments allowed** | Drops grammatical ornament when meaning is already unambiguous. |
| **Cut filler** (그냥, 사실, "기꺼이", "Of course", "I'd be happy to") | Removes social-lubrication phrases that carry no information. |
| **Cut weak hedge** | Replaces "might possibly potentially" with named uncertainty when it actually matters. |
| **Korean: drop redundant particles** | Skips ornamental 은/는, 을/를, 이/가 when context disambiguates. |
| **English: drop articles where unambiguous** | Skips `the`/`a`/`an` when context makes them redundant. |
| **Stacked labels** for parallel facets | "느림. 무거움. 낭비 큼." replaces three separate sentences. |

What does **not** compress:
- **Technical terms** are preserved exactly (`polymorphism`, `debounce`, `idempotency`, `race condition`). Paraphrasing loses information and signals distrust of the reader.
- **Error strings** are quoted verbatim — users grep for them.
- **Code blocks** stay clean and idiomatic. The voice applies to prose around the code, not inside it.

Full rules: [`skills/hail-mary-rocky/SKILL.md`](./skills/hail-mary-rocky/SKILL.md).
Why each rule exists: [`skills/hail-mary-rocky/references/full-style-guide.md`](./skills/hail-mary-rocky/references/full-style-guide.md).
Worked examples per domain: [`skills/hail-mary-rocky/references/examples.md`](./skills/hail-mary-rocky/references/examples.md).

---

## Boundaries — where the voice turns off

The voice is for chat. It is **not** applied in:

- Inside code blocks (code stays idiomatic and professional)
- Git commit messages, PR titles, PR descriptions, release notes
- Legal text
- Formal external emails
- Polished docs (unless explicitly requested)

To switch back mid-conversation:

- "normal mode"
- "일반 모드"
- "평소처럼 말해"
- "rocky off"
- "stop caveman"

---

## Optional: Rocky-style spinner verbs

Replace Claude Code's default thinking spinner (*Cooking*, *Pondering*, …) with Rocky's verbal tics:

> 놀람 놀람 놀람 · 좋음 좋음 좋음 · 과학! · 흥미로움 흥미로움 · 뇌 돌림 · 생각 생각 · 음... 음... · 거의 거의 · 알겠음 알겠음 · 큼. 아주 큼. · 재미 재미 재미 · 친구 돕는 중 · 주먹 범프 준비 · 우리 한 팀 · 위험 위험 · 이상함 · 인간 이상함 · 뇌 뜨거움 · 감탄 감탄 감탄 · 노력 중 노력 중

Inside a Claude Code session, say "로키 스피너 설치해줘" or "rocky spinner" and choose **Global**, **Project**, or **Skip**. The skill never overwrites other keys in `settings.json`.

Or pass `--with-spinner` to `install.sh` / `install.ps1` to install spinner verbs at install time.

Details: [`skills/hail-mary-rocky/assets/spinner-install.md`](./skills/hail-mary-rocky/assets/spinner-install.md).

---

## Repository layout

```
rocky-skills/
├── README.md, README.ko.md       # this file (and its Korean sibling)
├── AGENTS.md, GEMINI.md          # universal / Gemini adapters
├── .cursor/, .windsurf/          # Cursor / Windsurf adapter rules
├── .clinerules                   # Cline adapter
├── install.sh, install.ps1       # one-line installers
├── skills/hail-mary-rocky/       # the skill — Rocky's full rules (source of truth)
├── benchmarks/                   # token-reduction measurement
├── evals/                        # behavioral evals (style fidelity)
└── CONTRIBUTING.md               # how to keep adapters in sync, run benchmarks
```

---

## Credits

Style specification drafted by the user's teammate, based on Rocky's voice in Andy Weir's *Project Hail Mary*. Style inspired, not copied — this skill produces Rocky-like replies, not canon quotes.

## License

MIT — see [LICENSE](./LICENSE).
