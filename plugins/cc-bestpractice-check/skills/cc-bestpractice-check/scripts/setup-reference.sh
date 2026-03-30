#!/usr/bin/env bash
# リファレンスリポジトリのクローンまたは最新化
set -euo pipefail

REPO_DIR="${CLAUDE_PLUGIN_ROOT}/reference/claude-code-best-practice"

if [ -d "$REPO_DIR/.git" ]; then
  cd "$REPO_DIR" && git pull --ff-only
else
  mkdir -p "$(dirname "$REPO_DIR")"
  git clone https://github.com/shanraisshan/claude-code-best-practice.git "$REPO_DIR"
fi
