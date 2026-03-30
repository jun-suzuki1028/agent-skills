---
name: cc-bestpractice-check
description: "Claude Codeベストプラクティスチェック、設定チェック、bestpractice check、ベスプラ確認、config audit、設定監査"
version: 1.1.0
user-invocable: true
arguments:
  - name: project_path
    description: "チェック対象のプロジェクトパス（省略時はユーザーに確認）"
    required: false
---

# Best Practice Check

[claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) リポジトリをリファレンスとして、ユーザーのClaude Code設定を比較し、ギャップと改善提案をレポートする。

## 定数

- **リファレンスリポジトリ**: `${CLAUDE_PLUGIN_ROOT}/reference/claude-code-best-practice/`
- **グローバル設定**: `~/.claude/`
- **ベスプラドキュメント**: リファレンスリポジトリ内の `best-practice/`, `tips/`, `implementation/`, `reports/`

## 重要ルール: スコープの厳密な分離

**このスキルの最重要ルール。必ず守ること。**

### チェック対象がプロジェクトの場合

- **レポート対象**: プロジェクト設定のみ。グローバル設定の問題は「参考: グローバル設定への推奨」セクションで情報提供のみ
- **修正適用**: プロジェクトのファイルのみ変更可能。**グローバル設定は絶対に変更しない**
- **プロジェクトで利用していない機能への提案は不要**（例: MCP未使用なのに`.mcp.json`追加を提案しない）

### チェック対象がグローバルのみの場合

- **レポート対象**: グローバル設定のみ
- **修正適用**: グローバルのファイルのみ変更可能

### 重要度の区別

- **[GAP]**: 明確な問題や欠落（セキュリティリスク、動作に影響する設定ミス等）
- **[推奨]**: あると良いが必須ではないプラクティス（CLAUDE.local.md、settings.local.json等）
- プロジェクトが実際に使っている機能に対してのみ提案する

## Phase 0: セットアップ

### リファレンスリポジトリの準備

```bash
REPO_DIR="${CLAUDE_PLUGIN_ROOT}/reference/claude-code-best-practice"

if [ -d "$REPO_DIR/.git" ]; then
  cd "$REPO_DIR" && git pull --ff-only
else
  mkdir -p "$(dirname "$REPO_DIR")"
  git clone https://github.com/shanraisshan/claude-code-best-practice.git "$REPO_DIR"
fi
```

上記を Bash ツールで実行し、リファレンスを最新化する。

## Phase 1: チェック対象の決定

### 引数ありの場合

`$ARGUMENTS` にプロジェクトパスが指定されていれば、そのパスを対象プロジェクトとする。

### 引数なしの場合

AskUserQuestion ツールでユーザーに確認する:

> 「チェック対象を選んでください:」
> 1. **カレントディレクトリ（{CWD}）のプロジェクトをチェック**
> 2. **グローバル設定のみ** — `~/.claude/` 配下だけチェック

## Phase 2: 設定収集

以下のファイル/ディレクトリを読み取る。存在しないものはスキップ。

### グローバル設定（常に収集 — レポートのスコープは Phase 1 で決定済み）

| 対象 | パス |
|------|------|
| CLAUDE.md | `~/.claude/CLAUDE.md` |
| Settings | `~/.claude/settings.json` |
| Hooks | `~/.claude/hooks/` 配下のファイル一覧と内容 |
| Commands | `~/.claude/commands/` 配下のファイル一覧 |
| Agents | `~/.claude/agents/` 配下のファイル一覧 |
| Skills | `~/.claude/skills/` 配下のディレクトリ一覧 |

### プロジェクト設定（対象プロジェクトが指定された場合のみ）

| 対象 | パス |
|------|------|
| CLAUDE.md | `{project}/.claude/CLAUDE.md` または `{project}/CLAUDE.md` |
| Settings | `{project}/.claude/settings.json` |
| Commands | `{project}/.claude/commands/` |
| Agents | `{project}/.claude/agents/` |
| MCP設定 | `{project}/.mcp.json` |

**Phase 2.5: プロジェクトの実態把握**

プロジェクトが指定された場合、設定収集後にプロジェクトの実態を把握する:
- どの技術スタックを使っているか（CLAUDE.mdやpackage.json等から判断）
- どの機能を実際に利用しているか（MCP、hooks、commands、agents等）
- **利用していない機能に対するベスプラ提案はスキップする**

## Phase 3: ベストプラクティス読み込みと比較

カテゴリごとにリファレンスリポジトリの該当文書を読み、ユーザー設定と**意味的に**比較する。
完全一致を求めるのではなく、**欠落しているベストプラクティスや改善余地**を検出する。

### チェックカテゴリと参照元

| カテゴリ | リファレンス内の参照先 |
|---------|----------------------|
| CLAUDE.md構成・メモリ管理 | `best-practice/claude-memory.md`, `reports/claude-agent-memory.md` |
| Settings設定 | `best-practice/claude-settings.md`, `reports/claude-global-vs-project-settings.md` |
| Hooks活用 | `best-practice/` 内のhook関連, `.claude/hooks/` |
| Commands活用 | `best-practice/claude-commands.md`, `implementation/claude-commands-implementation.md` |
| Subagents活用 | `best-practice/claude-subagents.md`, `implementation/claude-subagents-implementation.md` |
| Skills活用 | `best-practice/claude-skills.md`, `implementation/claude-skills-implementation.md` |
| MCP設定 | `best-practice/claude-mcp.md` |
| 実践Tips | `tips/` 配下の全ファイル |

### 比較の観点

各カテゴリで以下を確認する:

1. **構造面** — 推奨されるファイル/セクションが存在するか
2. **内容面** — 推奨されるプラクティスが設定に反映されているか
3. **改善機会** — ベスプラで紹介されていて、ユーザーが未活用の機能・パターン

### フィルタリング原則

- **プロジェクトが実際に利用している機能**に対してのみチェック・提案する
- 利用していない機能の導入提案はしない（例: MCP未使用プロジェクトへの.mcp.json提案）
- 必須でないプラクティスは[推奨]として明示し、[GAP]とは区別する

### トークン節約

- リファレンスの全文は読まない。カテゴリごとに必要なファイルだけ Read する
- ユーザー設定もファイル一覧から必要なものだけ読む
- 問題なしの項目はレポートから省略する

## Phase 4: レポート出力

チェック対象のスコープに応じてレポート構造を変える。

### プロジェクト指定時のレポート形式

```markdown
## cc-bestpractice-check レポート

**対象**: {プロジェクト名}（プロジェクトスコープ）
**リファレンス**: claude-code-best-practice (commit: {hash}, {date})

---

### プロジェクト Settings
- **[GAP]** {ギャップの説明}
  - **提案**: {具体的な修正内容}
  - **参照**: {リファレンス内の該当ファイル}
- **[推奨]** {推奨事項の説明}
  - **提案**: {具体的な修正内容}
  - **参照**: {リファレンス内の該当ファイル}

### プロジェクト CLAUDE.md
...

### プロジェクト Agents
...

---

**ギャップ合計**: {N}件（GAP: {n1}件、推奨: {n2}件）

---

### 参考: グローバル設定への推奨（情報提供のみ・このスキル実行では適用しません）

- {グローバル側で改善すると良い点}
```

### グローバル指定時のレポート形式

```markdown
## cc-bestpractice-check レポート

**対象**: グローバル設定
**リファレンス**: claude-code-best-practice (commit: {hash}, {date})

---

### Settings
- **[GAP]** / **[推奨]** ...

### Hooks
...

---

**ギャップ合計**: {N}件（GAP: {n1}件、推奨: {n2}件）
```

ギャップが0件の場合:
```
全カテゴリでベストプラクティスに準拠しています。
```

## Phase 5: 修正適用

レポート出力後、AskUserQuestion ツールでユーザーに確認する:

> 「修正を適用しますか？」
> 1. **すべて適用** — レポート内の全提案を適用
> 2. **選択して適用** — 適用する提案を番号で選択
> 3. **適用しない** — レポートの確認のみで終了

「選択して適用」の場合は、適用する提案の番号をユーザーに入力してもらう。

### 適用時のスコープ制限（厳守）

- **プロジェクト指定時**: プロジェクトのファイルのみ変更する。グローバルファイルは一切変更しない
- **グローバル指定時**: グローバルのファイルのみ変更する
- 「参考: グローバル設定への推奨」セクションの内容は適用対象外

適用時は Edit ツールで既存ファイルを修正、または Write ツールで新規ファイルを作成する。
