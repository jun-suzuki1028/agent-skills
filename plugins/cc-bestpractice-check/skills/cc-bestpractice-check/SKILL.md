---
name: cc-bestpractice-check
description: "This skill should be used when the user asks to \"ベスプラチェックして\", \"ベストプラクティスチェック\", \"設定を監査して\", \"CLAUDE.mdを見直したい\", \"Claude Codeの設定がベストプラクティスに沿っているか確認\", \"設定チェック\", \"設定の見直し\", \"CLAUDE.mdのチェック\", \"CC設定の診断\". グローバル/プロジェクトのClaude Code設定を公式ドキュメントと比較し、ギャップと改善提案をレポートする。"
version: 2.0.0
user-invocable: true
arguments:
  - name: project_path
    description: "チェック対象のプロジェクトパス（省略時はユーザーに確認）"
    required: false
---

# Best Practice Check

Anthropic公式ドキュメント（code.claude.com）をリファレンスとして、ユーザーのClaude Code設定を比較し、ギャップと改善提案をレポートする。

## ランタイム変数

- `$ARGUMENTS` — ユーザーがスキル呼び出し時に渡した引数文字列

## 公式ドキュメントURL

ベストプラクティスの参照元として、以下の公式ドキュメントを WebFetch で取得する。
`.md` 拡張子付きURLを使用すること（HTMLタグが含まれず効率的）。

| カテゴリ | URL |
|---------|-----|
| Best Practices（総合） | `https://code.claude.com/docs/en/best-practices.md` |
| CLAUDE.md | `https://code.claude.com/docs/en/memory.md` |
| Settings | `https://code.claude.com/docs/en/settings.md` |
| Hooks | `https://code.claude.com/docs/en/hooks-guide.md` |
| Skills | `https://code.claude.com/docs/en/skills.md` |
| Subagents | `https://code.claude.com/docs/en/sub-agents.md` |
| MCP | `https://code.claude.com/docs/en/mcp.md` |
| Commands | `https://code.claude.com/docs/en/slash-commands.md` |
| Plugins | `https://code.claude.com/docs/en/plugins.md` |
| Permissions | `https://code.claude.com/docs/en/permissions.md` |
| .claudeディレクトリ構造 | `https://code.claude.com/docs/en/claude-directory.md` |
| Permission modes / Sandboxing | `https://code.claude.com/docs/en/permission-modes.md` |
| Status line | `https://code.claude.com/docs/en/statusline.md` |
| GitHub Actions / CI | `https://code.claude.com/docs/en/github-actions.md` |
| Environment variables | `https://code.claude.com/docs/en/env-vars.md` |

## 重要ルール: スコープの厳密な分離

**このスキルの最重要ルール。必ず守ること。**

### チェック対象がプロジェクトの場合

- **レポート対象**: プロジェクト設定のみ。グローバル設定の問題は「参考: グローバル設定への推奨」セクションで情報提供のみ
- **修正適用**: プロジェクトのファイルのみ変更可能。**グローバル設定は絶対に変更しない**

### チェック対象がグローバルのみの場合

- **レポート対象**: グローバル設定のみ
- **修正適用**: グローバルのファイルのみ変更可能

### 重要度の分類（全フェーズ共通の定義）

以下の分類はレポート出力・フィルタリング・比較のすべてで適用する唯一の定義:

| ラベル | 対象 | 意味 |
|--------|------|------|
| **[GAP]** | 利用中の機能 | 明確な問題や欠落（セキュリティリスク、動作に影響する設定ミス等） |
| **[推奨]** | 利用中の機能 | あると良いが必須ではないプラクティス（CLAUDE.local.md、settings.local.json等） |
| **[参考]** | 未利用の機能 | 有益そうな機能・パターンの情報提供。導入を強く勧めない |
| *(省略)* | 未利用かつ関連性の薄い機能 | レポートに含めない |

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
| Settings (local) | `~/.claude/settings.local.json` |
| Hooks | `~/.claude/hooks/` 配下のファイル一覧と内容 |
| Commands | `~/.claude/commands/` 配下のファイル一覧 |
| Agents | `~/.claude/agents/` 配下のファイル一覧 |
| Skills | `~/.claude/skills/` 配下のディレクトリ一覧 |
| Plugins | `~/.claude/plugins/` 配下のディレクトリ一覧 |
| .claudeディレクトリ全体 | `~/.claude/` のディレクトリ構造 |

### プロジェクト設定（対象プロジェクトが指定された場合のみ）

| 対象 | パス |
|------|------|
| CLAUDE.md | `{project}/.claude/CLAUDE.md` または `{project}/CLAUDE.md` |
| Settings | `{project}/.claude/settings.json` |
| Settings (local) | `{project}/.claude/settings.local.json` |
| Commands | `{project}/.claude/commands/` |
| Agents | `{project}/.claude/agents/` |
| Skills | `{project}/.claude/skills/` |
| MCP設定 | `{project}/.mcp.json` |
| GitHub Actions | `{project}/.github/workflows/` 内のClaude Code関連ワークフロー |
| .claudeディレクトリ全体 | `{project}/.claude/` のディレクトリ構造 |

## Phase 3: プロジェクトの実態把握

プロジェクトが指定された場合、設定収集後にプロジェクトの実態を把握する:

- どの技術スタックを使っているか（CLAUDE.md、package.json、pyproject.toml、Cargo.toml、go.mod、pom.xml等から判断）
- どの機能を実際に利用しているか（MCP、hooks、commands、agents、skills等）
- 利用状況に応じて「重要度の分類」テーブルのラベルを適用する

## Phase 4: 公式ドキュメント取得と比較

チェック対象の利用状況に基づき、関連する公式ドキュメントのみを WebFetch で取得し、ユーザー設定と**意味的に**比較する。
完全一致を求めるのではなく、**欠落しているベストプラクティスや改善余地**を検出する。

### チェックカテゴリと参照元

| カテゴリ | 取得する公式ドキュメント | 検証対象 |
|---------|----------------------|---------|
| 総合（必須取得） | Best Practices | — |
| .claudeディレクトリ構造 | .claudeディレクトリ構造 | ディレクトリ構成が推奨パターンに沿っているか |
| CLAUDE.md構成・メモリ管理 | CLAUDE.md | 配置場所、内容の簡潔さ、@importの活用 |
| Settings設定 | Settings, Permissions | グローバル/プロジェクト分離、permission rules |
| Permission modes / Sandboxing | Permission modes / Sandboxing | auto mode、sandbox設定の有無 |
| Hooks活用 | Hooks | フォーマッタ・リンター等の自動化設定 |
| Commands活用 | Commands | カスタムコマンドの有無と構成 |
| Subagents活用 | Subagents | カスタムエージェントの有無と構成 |
| Skills活用 | Skills | スキルの有無と構成 |
| MCP設定 | MCP | MCP接続の有無と構成 |
| Plugins活用 | Plugins | プラグインの有無 |
| Status line | Status line | コンテキスト監視用ステータスライン設定 |
| GitHub Actions / CI | GitHub Actions / CI | Claude Code CI連携の設定有無 |
| Environment variables | Environment variables | 推奨env var設定 |

### 比較の観点

各カテゴリで以下を確認する:

1. **構造面** — 推奨されるファイル/セクションが存在するか
2. **内容面** — 推奨されるプラクティスが設定に反映されているか
3. **改善機会** — 「重要度の分類」テーブルに基づきラベル付けする

### トークン節約

- 全ドキュメントを一括取得しない。利用中の機能に関連するドキュメントのみ WebFetch する
- Best Practices（総合）は必ず取得し、他はユーザーの利用状況に応じて取得する
- ユーザー設定もファイル一覧から必要なものだけ読む
- 問題なしの項目はレポートから省略する

## Phase 5: レポート出力

チェック対象のスコープに応じてレポート構造を変える。

### プロジェクト指定時のレポート形式

```markdown
## cc-bestpractice-check レポート

**対象**: {プロジェクト名}（プロジェクトスコープ）
**リファレンス**: Claude Code公式ドキュメント（code.claude.com）

---

### プロジェクト Settings
- **[GAP]** {ギャップの説明}
  - **提案**: {具体的な修正内容}
  - **参照**: {公式ドキュメントURL}
- **[推奨]** {推奨事項の説明}
  - **提案**: {具体的な修正内容}
  - **参照**: {公式ドキュメントURL}

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
**リファレンス**: Claude Code公式ドキュメント（code.claude.com）

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

## Phase 6: 修正適用

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
