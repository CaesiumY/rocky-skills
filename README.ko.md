# rocky-skills

> Rocky의 압축된 말투로 LLM 출력 토큰을 ~30~60% 줄입니다.
> 판단 먼저, 프래그먼트 허용, 필러 제거, 기술 정확성 유지.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/agents-6-blue)](#멀티-에이전트-지원)
[![English README](https://img.shields.io/badge/English-README.md-informational)](./README.md)

Rocky는 앤디 위어의 『프로젝트 헤일메리』에 등장하는 외계인 엔지니어입니다. 그의 번역체 — 짧은 프래그먼트, 판단 먼저, 필러 없음, 기술 정확성 유지 — 는 LLM 출력 압축 알고리즘과 거의 1:1로 매핑됩니다. 이 레포는 그 말투를 Claude Code 스킬로 패키징하고, Cursor, Codex, Gemini CLI, Windsurf, Cline용 어댑터를 함께 제공합니다.

English README: [README.md](./README.md)

---

## 설치

```bash
curl -fsSL https://raw.githubusercontent.com/CaesiumY/rocky-skills/main/install.sh | bash
```

PowerShell (Windows):

```powershell
irm https://raw.githubusercontent.com/CaesiumY/rocky-skills/main/install.ps1 | iex
```

Claude Code만 설치하려면 skills CLI 사용:

```bash
npx skills add CaesiumY/rocky-skills
```

다른 에이전트용 어댑터 복사 안내는 [멀티 에이전트 지원](#멀티-에이전트-지원) 섹션 참고.

---

## 왜 출력 토큰만 줄이나

Claude의 현재 모델 라인업에서 **출력 토큰 가격은 입력 토큰의 약 5배**입니다 — Sonnet 4.6은 입력 $3/M vs 출력 $15/M, Haiku 4.5는 $1/M vs $5/M, Opus 4.7은 $5/M vs $25/M. 비율은 어디서나 동일합니다. 응답이 두 배 길어진다고 비용이 두 배가 되는 게 아니라, 긴 절반이 청구서를 지배합니다.

이 프로젝트가 의도적으로 **출력** 압축에만 집중하는 이유입니다. 프롬프트, 시스템 메시지, 툴 설명 같은 입력 측은 건드리지 않습니다 (예컨대 [caveman](https://github.com/juliusbrussee/caveman)의 MCP 미들웨어가 작동하는 영역). Rocky는 같은 답을 더 짧게 만들 뿐인데, 거기서 절감된 토큰 하나는 입력 측 토큰 하나보다 ~5배 가치가 있습니다.

긴 응답·에이전트 루프·채팅 중심 워크플로에서 청구서가 큰 사람일수록 출력 압축의 레버리지가 큽니다.

---

## Before / After

같은 프롬프트 *"React 컴포넌트가 계속 리렌더링되는데 원인이 뭐야?"*, 같은 모델.

**Rocky 없이** (~140 출력 토큰):

> 컴포넌트가 부모 업데이트 때마다 리렌더링되는 이유는 매 렌더 사이클마다 새로운 객체 참조를 생성하고 있기 때문일 가능성이 높습니다. 인라인 객체를 prop으로 전달하면 부모가 리렌더될 때마다 React가 그것을 새로운 값으로 취급하므로 자식 컴포넌트도 함께 리렌더됩니다. 이를 해결하려면 객체를 `useMemo` 훅으로 감싸 같은 참조가 렌더 사이에 재사용되도록 하거나, 객체를 컴포넌트 외부로 빼서 모듈 스코프에 한 번만 정의되도록 할 수 있습니다.

**Rocky 적용** (~52 출력 토큰):

> 매 렌더마다 새 객체 ref 생성. 인라인 객체 prop = 새 ref = 리렌더. `useMemo`로 감쌈. 아니면 컴포넌트 밖 상수로 뺌. React DevTools Profiler로 재렌더 원인 확인.

같은 진단, 같은 해법, ~63% 적은 출력 토큰.

---

## 벤치마크

고정된 프롬프트 세트로 baseline(시스템 프롬프트 없음) 대비 출력 토큰 측정 — **실제 Anthropic API 호출로 측정**한 값입니다. 응답의 `usage.output_tokens`를 직접 기록한 것이지 로컬 토크나이저 추정이나 합성 데이터가 아닙니다. 원시 측정값은 [`benchmarks/results.json`](./benchmarks/results.json)에 커밋되어 있습니다. 방법론은 [`benchmarks/README.md`](./benchmarks/README.md). 아래 표는 `python benchmarks/render_readme_table.py`가 자동 생성합니다.

<!-- benchmarks:start -->
| 프롬프트 | Baseline | Rocky | 절감 |
|---|---:|---:|---:|
| `react-rerender` | 1024 | 358 | -65.0% |
| `support-overworked` | 53 | 77 | +45.3% |
| `arch-monolith-coupling` | 1023 | 390 | -61.9% |
| `sql-query-optimization` | 1024 | 429 | -58.1% |
| `git-rebase-conflict` | 595 | 329 | -44.7% |
| `ts-type-narrowing` | 851 | 402 | -52.8% |
| `short-yes-no` | 72 | 49 | -31.9% |
| `python-listcomp-vs-generator` | 724 | 329 | -54.6% |

**평균 절감률: −40.5%** (토큰 가중: −56.0%) — 8개 프롬프트, 모델 `claude-sonnet-4-6`.

_2026-05-04에 Anthropic API로 직접 측정 — 응답의 `usage.output_tokens` 값, 추정 없음._

<!-- benchmarks:end -->

직접 실행:

```bash
cp benchmarks/.env.example .env       # ANTHROPIC_API_KEY 세팅
pip install -r benchmarks/requirements.txt
python benchmarks/run.py
python benchmarks/render_readme_table.py
```

---

## 활성화

**6개 에이전트 모두 디폴트 always-on.** 어댑터 파일을 프로젝트에 두거나 인스톨러를 돌리면 모든 응답이 Rocky 보이스 — 매 세션 트리거 불필요. 경계(코드 블록·커밋·법률 텍스트)는 `SKILL.md`의 규칙이 자동 처리하므로 always-on이라도 안전.

| 에이전트 | 설치 후 디폴트 상태 |
|---|---|
| Claude Code | always-on (`install.sh` / `install.ps1`이 규칙을 `CLAUDE.md`에 병합) |
| Cursor | always-on (`.cursor/rules/rocky.md`의 `alwaysApply: true`) |
| Windsurf | always-on (`trigger: always_on`) |
| Cline | always-on (`.clinerules` 자동 로드) |
| Codex / 범용 | always-on (`AGENTS.md` 자동 로드) |
| Gemini CLI | always-on (`GEMINI.md` 자동 로드) |

### 끄기와 다시 켜기

끄기 스위치는 보이스가 부적절한 일회성 작업(긴 문서, 공식 이메일)을 위함:

- 현재 세션 한정으로 끄기: `normal mode` / `일반 모드` / `rocky off` / `stop caveman`
- 다시 켜기: `rocky` / `로키` / `rocky mode` / `caveman mode` / `헤일메리`

새 세션은 다시 always-on 상태로 시작.

### CLAUDE.md 머지를 건너뛰고 싶다면 (Claude Code만)

Claude Code 스킬을 순수 트리거 기반(skill description 매칭 시에만 자동 invoke)으로 두고 싶으면 인스톨러에 `--skip-claude-md` 플래그:

```bash
curl -fsSL https://raw.githubusercontent.com/CaesiumY/rocky-skills/main/install.sh | bash -s -- --skip-claude-md
# PowerShell
iex "& { $(irm https://raw.githubusercontent.com/CaesiumY/rocky-skills/main/install.ps1) } -SkipClaudeMd"
```

인스톨러는 `CLAUDE.md` 안에 마커 블록(`<!-- rocky-skills:start --> ... <!-- rocky-skills:end -->`)을 관리합니다. 재실행 시 블록을 in-place로 교체하므로 중복되지 않습니다. 되돌리려면 블록을 수동 삭제.

---

## 멀티 에이전트 지원

Rocky의 규칙은 [`skills/hail-mary-rocky/SKILL.md`](./skills/hail-mary-rocky/SKILL.md)에 정의되어 있습니다. 각 에이전트는 그 규칙을 자신의 형식으로 응축한 어댑터를 사용합니다.

| 에이전트 | 어댑터 파일 |
|---|---|
| Claude Code | [`skills/hail-mary-rocky/`](./skills/hail-mary-rocky/) |
| Codex / 범용 | [`AGENTS.md`](./AGENTS.md) |
| Cursor | [`.cursor/rules/rocky.md`](./.cursor/rules/rocky.md) |
| Gemini CLI | [`GEMINI.md`](./GEMINI.md) |
| Windsurf | [`.windsurf/rules/rocky.md`](./.windsurf/rules/rocky.md) |
| Cline | [`.clinerules`](./.clinerules) |

어댑터는 진실의 원천이 아닌 응축 사본입니다. [`SKILL.md`](./skills/hail-mary-rocky/SKILL.md)가 바뀌면 [`CONTRIBUTING.md`](./CONTRIBUTING.md)의 동기화 절차를 따릅니다.

---

## 동작 원리 — Rocky 규칙을 압축 알고리즘으로 보기

Rocky의 번역체 스타일은 LLM 출력 압축 알고리즘과 거의 일대일로 매핑됩니다. 각 규칙이 어떤 이유로 토큰을 줄이는지:

| 규칙 | 토큰 절감 이유 |
|---|---|
| **판단 먼저** | 답이 앞으로 오니 모델이 만들어내던 긴 도입부가 사라짐. |
| **짧은 문장 / 프래그먼트 허용** | 의미가 명확할 때 문법적 장식 제거. |
| **필러 제거** (그냥, 사실, "기꺼이", "Of course") | 정보 없는 사회적 윤활어 삭제. |
| **약한 헤지 제거** | "혹시 약간 가능할 수도" 같은 어휘를 실제 불확실성이 있을 때만 명시. |
| **한국어: 조사 축약** | 문맥상 불필요한 은/는, 을/를, 이/가 생략. |
| **영어: 문맥 명확하면 article 생략** | 불필요한 `the`/`a`/`an` 제거. |
| **스택 라벨**(병렬 진단) | "느림. 무거움. 낭비 큼." — 세 문장이 세 단어로. |

압축하지 **않는** 것:
- **기술 용어**는 그대로 보존(`polymorphism`, `debounce`, `idempotency`, `race condition`). 의역은 정보 손실이고 독자에 대한 불신 신호.
- **에러 메시지**는 backtick 안에 원문 그대로 — 사용자가 grep 함.
- **코드 블록**은 깨끗하고 관용적으로. 말투는 코드 주변 산문에만 적용.

전체 규칙: [`skills/hail-mary-rocky/SKILL.md`](./skills/hail-mary-rocky/SKILL.md).
규칙별 이유: [`skills/hail-mary-rocky/references/full-style-guide.md`](./skills/hail-mary-rocky/references/full-style-guide.md).
도메인별 예시: [`skills/hail-mary-rocky/references/examples.md`](./skills/hail-mary-rocky/references/examples.md).

---

## 경계 — 말투를 *끄는* 곳

이 말투는 채팅용입니다. 다음 맥락에서는 적용하지 **않습니다**:

- 코드 블록 내부 (코드 자체는 관용적이고 전문적으로)
- Git 커밋 메시지, PR 제목/본문, 릴리즈 노트
- 법률 문서
- 공식 외부 이메일
- 세련된 문서 (명시적 요청 없으면)

대화 중 일반 모드로 복귀:

- "normal mode"
- "일반 모드"
- "평소처럼 말해"
- "rocky off"
- "stop caveman"

---

## 선택: Rocky 스타일 스피너 동사

Claude Code의 기본 스피너(*Cooking*, *Pondering* 등)를 Rocky의 말버릇으로 교체:

> 놀람 놀람 놀람 · 좋음 좋음 좋음 · 과학! · 흥미로움 흥미로움 · 뇌 돌림 · 생각 생각 · 음... 음... · 거의 거의 · 알겠음 알겠음 · 큼. 아주 큼. · 재미 재미 재미 · 친구 돕는 중 · 주먹 범프 준비 · 우리 한 팀 · 위험 위험 · 이상함 · 인간 이상함 · 뇌 뜨거움 · 감탄 감탄 감탄 · 노력 중 노력 중

Claude Code 세션에서 "로키 스피너 설치해줘" 또는 "rocky spinner"라고 말하면 **전역**, **프로젝트**, **건너뜀** 중 선택. 스킬은 `settings.json`의 다른 키를 절대 건드리지 않습니다.

또는 `install.sh` / `install.ps1`에 `--with-spinner` 플래그로 설치 시점에 함께 적용.

상세: [`skills/hail-mary-rocky/assets/spinner-install.md`](./skills/hail-mary-rocky/assets/spinner-install.md).

---

## 레포 구조

```
rocky-skills/
├── README.md, README.ko.md       # 이 파일과 한국어 짝
├── AGENTS.md, GEMINI.md          # 범용 / Gemini 어댑터
├── .cursor/, .windsurf/          # Cursor / Windsurf 룰
├── .clinerules                   # Cline 어댑터
├── install.sh, install.ps1       # 원라인 인스톨러
├── skills/hail-mary-rocky/       # 스킬 — Rocky 전체 규칙 (진실의 원천)
├── benchmarks/                   # 토큰 절감 측정
├── evals/                        # 행동 evals (스타일 정확도)
└── CONTRIBUTING.md               # 어댑터 동기화·벤치마크 실행 가이드
```

---

## 원작자 주의사항

- 스타일은 **영감을 받은 것**이지 **원작 그대로의 복사**가 아닙니다
- 소설 원문 대사 인용 금지
- 패러디/우가우가/베이비 토크 금지
- Rocky는 문법이 거칠 뿐 **머리는 날카롭다** — 이 균형이 핵심

## 라이선스

MIT — [LICENSE](./LICENSE) 참고.
