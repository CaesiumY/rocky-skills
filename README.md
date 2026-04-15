# hail-mary-rocky

A skill that makes Claude reply in the voice of Rocky from Andy Weir's *Project Hail Mary*.
Blunt diagnosis. Compressed sentences. Technical substance intact. Loyal heart.

Korean README: [README.ko.md](./README.ko.md)

---

## What it does

This skill switches Claude's reply voice into Rocky's translated-alien-engineer style:

- Verdict → cause → fix → next step
- Short fragments, no filler, no weak hedging
- Technical terms and code blocks kept exact
- Korean: slightly reduced particles, never dumbed down
- Warmth expressed through concrete action, not prose

It is **style over substance: false**. Technical correctness still wins. Style only shapes the surface.

---

## Install

### Option 1 — via skills.sh (recommended)

```bash
npx skills add CaesiumY/rocky-skills
```

The `skills` CLI downloads the skill and drops it into your Claude Code skills directory. If you fork this repo, replace `CaesiumY` with your own GitHub username.

### Option 2 — from a local clone

```bash
git clone https://github.com/CaesiumY/rocky-skills.git
npx skills add ./rocky-skills
```

Useful when developing locally or trying the skill before publishing.

### Option 3 — manual copy

```bash
cp -r skills/hail-mary-rocky ~/.claude/skills/
```

Works in any environment without the `skills` CLI.

---

## Trigger phrases

Any of these will invoke the skill in a Claude Code session:

- "rocky voice", "rocky mode", "caveman mode"
- "hail mary rocky", "헤일메리"
- "로키", "로키 말투", "로키 모드", "로키처럼 답해"

The skill is intentionally eager to trigger — style skills are easy to under-invoke.

---

## Style summary

| Rule | Example |
|---|---|
| Verdict first | `계산 틀림. 열 손실 반영 안 함. 식 다시 짬.` |
| Fragments allowed | `가능함. 위험함. 수정 필요.` |
| Technical terms exact | `문제 polymorphism 아님. lifetime 관리 문제.` |
| Physical metaphors | `얼굴에서 스트레스 누수 보임.` |
| Repetition for emphasis | `좋음 좋음. / 위험함 위험함.` |

Full rules: [`skills/hail-mary-rocky/SKILL.md`](./skills/hail-mary-rocky/SKILL.md)
Why each rule exists: [`skills/hail-mary-rocky/references/full-style-guide.md`](./skills/hail-mary-rocky/references/full-style-guide.md)
Worked examples per domain: [`skills/hail-mary-rocky/references/examples.md`](./skills/hail-mary-rocky/references/examples.md)

---

## Optional: Rocky-style spinner verbs

Replace Claude Code's thinking spinner (*Cooking*, *Pondering*, …) with Rocky's verbal tics:

> 놀람 놀람 놀람 · 좋음 좋음 좋음 · 과학! · 흥미로움 흥미로움 · 뇌 돌림 · 생각 생각 · 음... 음... · 거의 거의 · 알겠음 알겠음 · 큼. 아주 큼. · 재미 재미 재미 · 친구 돕는 중 · 주먹 범프 준비 · 우리 한 팀 · 위험 위험 · 이상함 · 인간 이상함 · 뇌 뜨거움 · 감탄 감탄 감탄 · 노력 중 노력 중

Inside a Claude session, say "로키 스피너 설치해줘" or "rocky spinner" and choose:

1. **Global** — merged into `~/.claude/settings.json`, applies everywhere
2. **Project** — merged into `.claude/settings.json` of the current project
3. **Skip** — keep the default Claude Code spinner

The skill never overwrites other keys in `settings.json`.

Details: [`skills/hail-mary-rocky/assets/spinner-install.md`](./skills/hail-mary-rocky/assets/spinner-install.md)

---

## Boundaries — where Rocky voice turns *off*

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

---

## Credits

Style specification drafted by the user's teammate, based on Rocky's voice in Andy Weir's *Project Hail Mary*. Style inspired, not copied — this skill produces Rocky-like replies, not canon quotes.

## License

MIT — see [LICENSE](./LICENSE).
