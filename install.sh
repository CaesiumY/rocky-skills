#!/usr/bin/env bash
# rocky-skills installer (Linux / macOS / WSL / Git Bash)
#
# Installs the hail-mary-rocky Claude Code skill. Other agents (Cursor, Codex,
# Gemini, Windsurf, Cline) are project-scoped — copy their adapter files into
# the project root manually. See README.md > Multi-agent support.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/CaesiumY/rocky-skills/main/install.sh | bash
#   bash install.sh --target=project          # install into ./.claude/skills/ instead of ~/.claude/skills/
#   bash install.sh --with-spinner            # also merge spinner verbs into settings.json
#   bash install.sh --ref=v1.2.3              # pin to a tag/branch (default: main)

set -euo pipefail

REPO="CaesiumY/rocky-skills"
REF="main"
TARGET="global"
WITH_SPINNER=0

for arg in "$@"; do
  case "$arg" in
    --target=project) TARGET="project" ;;
    --target=global)  TARGET="global" ;;
    --with-spinner)   WITH_SPINNER=1 ;;
    --ref=*)          REF="${arg#--ref=}" ;;
    -h|--help)
      sed -n '2,15p' "$0" | sed 's/^# //; s/^#$//'
      exit 0
      ;;
    *)
      echo "unknown arg: $arg" >&2
      exit 2
      ;;
  esac
done

if [ "$TARGET" = "project" ]; then
  SKILLS_DIR="$PWD/.claude/skills"
  SETTINGS_FILE="$PWD/.claude/settings.json"
else
  SKILLS_DIR="${HOME}/.claude/skills"
  SETTINGS_FILE="${HOME}/.claude/settings.json"
fi

WORK_DIR="$(mktemp -d -t rocky-skills.XXXXXX)"
trap 'rm -rf "$WORK_DIR"' EXIT

TARBALL_URL="https://codeload.github.com/${REPO}/tar.gz/refs/heads/${REF}"
echo "↓ downloading ${REPO}@${REF}"
curl -fsSL "$TARBALL_URL" -o "$WORK_DIR/repo.tar.gz"
tar -xzf "$WORK_DIR/repo.tar.gz" -C "$WORK_DIR"
EXTRACTED_DIR="$(find "$WORK_DIR" -maxdepth 1 -type d -name 'rocky-skills-*' | head -n1)"
if [ -z "$EXTRACTED_DIR" ] || [ ! -d "$EXTRACTED_DIR/skills/hail-mary-rocky" ]; then
  echo "ERROR: could not find skills/hail-mary-rocky in tarball" >&2
  exit 1
fi

mkdir -p "$SKILLS_DIR"
DEST="$SKILLS_DIR/hail-mary-rocky"
rm -rf "$DEST"
cp -r "$EXTRACTED_DIR/skills/hail-mary-rocky" "$DEST"
echo "✔ installed skill -> $DEST/"

if [ "$WITH_SPINNER" = "1" ]; then
  SPINNER_SRC="$EXTRACTED_DIR/skills/hail-mary-rocky/assets/spinner-verbs.json"
  if [ ! -f "$SPINNER_SRC" ]; then
    echo "WARN: $SPINNER_SRC missing, skipping spinner install" >&2
  elif command -v jq >/dev/null 2>&1; then
    mkdir -p "$(dirname "$SETTINGS_FILE")"
    if [ -f "$SETTINGS_FILE" ]; then
      tmp="$(mktemp)"
      jq -s '.[0] * .[1]' "$SETTINGS_FILE" "$SPINNER_SRC" > "$tmp"
      cat "$tmp" > "$SETTINGS_FILE"
      rm -f "$tmp"
    else
      cat "$SPINNER_SRC" > "$SETTINGS_FILE"
    fi
    echo "✔ merged spinner verbs into $SETTINGS_FILE"
  else
    echo "WARN: jq not found — skipping spinner merge."
    echo "      install jq, or run inside Claude Code: 'rocky spinner'"
  fi
fi

cat <<EOF

Done.

Other agents (project-scoped — copy these files into your project root):

  Cursor     → .cursor/rules/rocky.md
  Windsurf   → .windsurf/rules/rocky.md
  Cline      → .clinerules
  Codex etc. → AGENTS.md
  Gemini CLI → GEMINI.md

Trigger phrases: "rocky", "로키", "rocky mode", "caveman mode", "헤일메리".
Full rules: $SKILLS_DIR/hail-mary-rocky/SKILL.md
EOF
