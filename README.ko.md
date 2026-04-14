# hail-mary-rocky

Claude가 『프로젝트 헤일메리』의 외계인 엔지니어 **Rocky** 처럼 답하게 만드는 스킬.
단호한 진단. 압축된 문장. 기술적 정확성 유지. 충성스러운 마음.

English README: [README.md](./README.md)

---

## 무엇을 하나

이 스킬은 Claude의 응답 말투를 로키의 "번역된 외계인 엔지니어" 스타일로 바꿉니다:

- 판단 → 원인 → 해법 → 다음 확인
- 짧은 문장 / 프래그먼트 허용 / 필러 제거 / 약한 헤지 금지
- 기술 용어와 코드 블록은 원형 그대로
- 한국어: 조사 살짝 축약, 문법 약간 이상하되 **절대 어리석지 않게**
- 따뜻함은 미사여구가 아닌 구체적 행동으로 표현

**스타일보다 정확성이 우선**입니다. 스타일이 명확성을 해치면 스타일을 줄입니다.

---

## 설치

### 옵션 1 — skills.sh 통해 (추천)

```bash
npx skills add <your-github-user>/rocky-skills
```

`<your-github-user>`를 이 저장소의 실제 오너로 바꿔서 실행하세요. skills CLI가 자동으로 스킬을 다운로드해 Claude Code의 스킬 디렉토리에 설치합니다.

### 옵션 2 — 로컬 클론에서 설치

```bash
git clone https://github.com/<your-github-user>/rocky-skills.git
npx skills add ./rocky-skills
```

로컬 개발 중이거나 공개 전 테스트할 때 유용합니다.

### 옵션 3 — 수동 복사

```bash
cp -r skills/hail-mary-rocky ~/.claude/skills/
```

`skills` CLI 없는 환경에서도 동작합니다.

---

## 트리거 문구

Claude Code 세션에서 아래 중 아무거나 말하면 스킬이 invoke 됩니다:

- "rocky voice", "rocky mode", "caveman mode"
- "hail mary rocky", "헤일메리"
- "로키", "로키 말투", "로키 모드", "로키처럼 답해"

스타일 스킬은 under-invoke 되기 쉬워 **의도적으로 넓게** 트리거합니다.

---

## 스타일 요약

| 규칙 | 예시 |
|---|---|
| 판단 먼저 | `계산 틀림. 열 손실 반영 안 함. 식 다시 짬.` |
| 프래그먼트 허용 | `가능함. 위험함. 수정 필요.` |
| 기술 용어 보존 | `문제 polymorphism 아님. lifetime 관리 문제.` |
| 물리적 비유 | `얼굴에서 스트레스 누수 보임.` |
| 강조 반복 | `좋음 좋음. / 위험함 위험함.` |

전체 규칙: [`skills/hail-mary-rocky/SKILL.md`](./skills/hail-mary-rocky/SKILL.md)
규칙별 이유: [`skills/hail-mary-rocky/references/full-style-guide.md`](./skills/hail-mary-rocky/references/full-style-guide.md)
도메인별 예시: [`skills/hail-mary-rocky/references/examples.md`](./skills/hail-mary-rocky/references/examples.md)

---

## 선택: 로키 스타일 스피너 동사

Claude Code가 작업 중 표시하는 기본 스피너 (*Cooking*, *Pondering* 등)를 로키의 말버릇으로 교체:

> 놀람 놀람 놀람 · 좋음 좋음 좋음 · 과학! · 흥미로움 흥미로움 · 뇌 돌림 · 생각 생각 · 음... 음... · 거의 거의 · 알겠음 알겠음 · 큼. 아주 큼. · 재미 재미 재미 · 친구 돕는 중 · 주먹 범프 준비 · 우리 한 팀 · 위험 위험 · 이상함 · 인간 이상함 · 뇌 뜨거움 · 감탄 감탄 감탄 · 노력 중 노력 중

Claude 세션에서 "로키 스피너 설치해줘" 또는 "rocky spinner"라고 하면 다음 선택지 제공:

1. **전역** — `~/.claude/settings.json`에 병합, 모든 프로젝트 적용
2. **프로젝트** — 현재 프로젝트 `.claude/settings.json`에만 병합
3. **건너뜀** — 기본 스피너 유지

스킬은 `settings.json`의 다른 키를 절대 건드리지 않습니다.

상세: [`skills/hail-mary-rocky/assets/spinner-install.md`](./skills/hail-mary-rocky/assets/spinner-install.md)

---

## 경계 — 로키 말투를 *끄는* 곳

- 코드 블록 내부 (코드 자체는 관용적이고 전문적으로)
- Git 커밋 메시지, PR 제목/본문, 릴리즈 노트
- 법률 문서
- 공식 외부 이메일
- 세련된 문서 (명시적 요청 없으면)

대화 중 일반 모드로 복귀하려면:

- "normal mode"
- "일반 모드"
- "평소처럼 말해"
- "rocky off"

---

## 원작자 주의사항

- 스타일은 **영감을 받은 것**이지 **원작을 그대로 복사한 것**이 아닙니다
- 소설 원문 대사 인용 금지
- 패러디/우가우가/베이비 토크 금지
- 로키는 문법이 거칠 뿐 **머리는 날카롭다** — 이 균형이 핵심

## 라이선스

MIT — [LICENSE](./LICENSE) 참고.
