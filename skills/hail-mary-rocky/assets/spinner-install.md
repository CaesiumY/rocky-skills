# Rocky Spinner Verbs — Install Guide

로키 스피너는 Claude Code가 작업 중 표시하는 단어(기본: *Cooking*, *Pondering* 등)를 로키의 말버릇으로 바꿉니다. 선택 사항입니다.

---

## 사용자에게 세 선택지 제시

사용자가 "로키 스피너 설치해줘", "spinner 바꿔줘", "rocky spinner" 같은 요청을 하면 다음 세 가지 옵션을 제시하고 하나 고르게 합니다:

### Option 1 — Global
대상: `~/.claude/settings.json`
영향: 모든 프로젝트에서 로키 스피너 사용
추천: 로키 말투를 자주 쓸 때

### Option 2 — Project only
대상: `<현재 프로젝트>/.claude/settings.json`
영향: 현재 프로젝트에서만 적용
추천: 한 프로젝트에서만 시험하고 싶을 때

### Option 3 — Skip
아무것도 안 함. 말투만 사용.

---

## 머지 절차 (Option 1 / 2 공통)

1. 대상 파일을 읽음. 없으면 빈 JSON `{}`로 시작.
2. 파일에 이미 `spinnerVerbs` 키가 있으면 **사용자에게 덮어쓸지 먼저 물어봄**. 다른 키(`model`, `theme`, `permissions` 등)는 절대 건드리지 않음.
3. `assets/spinner-verbs.json`의 `spinnerVerbs` 객체를 대상 파일의 최상위에 병합.
4. JSON 포맷 유지(들여쓰기 2칸). 기존 파일 인코딩/개행 보존.

### 예: 기존 settings.json이 이런 상태일 때

```json
{
  "model": "claude-sonnet-4-6",
  "theme": "dark"
}
```

### 머지 후

```json
{
  "model": "claude-sonnet-4-6",
  "theme": "dark",
  "spinnerVerbs": {
    "mode": "replace",
    "verbs": [
      "놀람 놀람 놀람",
      "좋음 좋음 좋음",
      "과학!",
      "흥미로움 흥미로움",
      "뇌 돌림",
      "생각 생각",
      "음... 음...",
      "거의 거의",
      "알겠음 알겠음",
      "큼. 아주 큼.",
      "재미 재미 재미",
      "친구 돕는 중",
      "주먹 범프 준비",
      "우리 한 팀",
      "위험 위험",
      "이상함",
      "인간 이상함",
      "뇌 뜨거움",
      "감탄 감탄 감탄",
      "노력 중 노력 중"
    ]
  }
}
```

---

## 주의 사항

- **덮어쓰기 확인 필수**: 기존 `spinnerVerbs`가 있으면 삭제/변경 전에 사용자 동의를 받음.
- **다른 키 보존**: settings.json은 여러 설정이 공존함. `spinnerVerbs` 외에는 손대지 않음.
- **백업 권장**: 불안하면 `cp settings.json settings.json.bak` 먼저.
- **JSON 유효성**: 머지 후 `python -m json.tool <file>` 등으로 파싱 가능한지 확인.

---

## 되돌리기

`spinnerVerbs` 키를 통째로 삭제하면 Claude Code 기본 동사로 돌아감. 또는 `mode`를 `"replace"` → `"append"`로 바꾸면 기본 동사 + 로키 동사 섞어 사용.

---

## 커스터마이즈

`verbs` 배열을 직접 편집해 원하는 항목 추가/제거 가능. 너무 길어지면 일부 동사가 드물게 노출됨. 사용자가 가장 좋아하는 10-15개만 남겨도 됨.
