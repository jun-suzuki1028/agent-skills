---
name: cc-daily-report
description: Claude Codeの作業履歴から日次レポートを生成する。「日報」「今日の作業」「daily report」などで呼び出し可能。
license: MIT
compatibility: Requires Python 3.11+. No external dependencies.
metadata:
  author: jun-suzuki1028
  version: "1.0.0"
---

# 日次作業レポート生成スキル

Claude Codeのセッション履歴を解析し、1日の作業内容をレポートとして生成する。

## 実行手順

### 1. セッションデータの取得

以下のスクリプトを実行してセッションデータを取得する:

```bash
python3 scripts/parse_sessions.py [日付]
```

- 日付を省略すると今日の日付
- 日付形式: `YYYY-MM-DD`
- スクリプトはこのスキルの `scripts/` ディレクトリにある

### 2. パーサー出力の構造

パーサーは以下の情報を提供する:

```json
{
  "date": "2026-02-04",
  "session_count": 10,
  "tag_summary": {"#Python": 5, "#AWS": 3},
  "timeline": {
    "day_range": "09:00-18:00",
    "project_durations": {"project-a": 4.5, "project-b": 2.0}
  },
  "sessions": [
    {
      "session_id": "f6c08b5c-076b-4397-ae0e-c4e083f81c3d",
      "project_name": "my-project",
      "time_range": "09:00-12:00",
      "commands": ["commit", "clean"],
      "subagents": ["Explore", "Bash"],
      "skills": ["worktree-development"],
      "sample_prompts": ["機能Aを実装して"],
      "prompt_count": 5,
      "tags": ["#Python", "#Test"]
    }
  ]
}
```

**セッション情報の読み方:**
- `commands`: 使用されたスラッシュコマンド（例: `/commit`, `/daily-morning`）
- `subagents`: Task toolで使用されたサブエージェントタイプ（例: `Explore`, `Bash`）
- `skills`: Skill toolで呼び出されたスキル名（例: `worktree-development`）
- `session_id`: セッションの一意識別子（`claude --resume <session_id>` で再開可能）
- `sample_prompts`: ユーザーが入力した主要なプロンプト（デフォルト最大1件、150文字まで）
- `prompt_count`: 意味のあるプロンプトの総数
- `tags`: 技術タグ（デフォルト最大3件）

**注意**: `timeline` は設定で無効化されている場合、出力に含まれない

### 3. 要約の生成（Claude Codeの役割）

各セッションについて、以下の情報から具体的な要約を生成する:

**要約生成のガイドライン:**

1. **コマンドがある場合**: コマンド名から作業内容を推測
   - 例: `commit` → 「コード変更のコミット」
   - 例: `daily-morning` → 「デイリーノートの作成」
   - 例: `code-review` → 「コードレビュー」

2. **サブエージェントがある場合**: サブエージェントタイプから作業の性質を推測
   - 例: `Explore` → 「コードベースの調査・分析」
   - 例: `Bash` → 「コマンド実行を伴う作業」
   - 例: `Plan` → 「実装計画の設計」

3. **スキルがある場合**: スキル名から作業内容を推測
   - 例: `worktree-development` → 「Worktreeによる並行開発」
   - 例: `cc-daily-report` → 「日次レポート生成」

4. **プロンプトから推測**: `sample_prompts` の内容を分析
   - 「〜を実装」「〜を追加」→ 実装作業
   - 「〜を修正」「〜を直して」→ バグ修正
   - 「〜を確認」「〜を調査」→ 調査・確認
   - 「ブログ」「記事」→ 執筆作業

5. **簡潔な表現**: 20文字以内で作業内容を表現
   - 良い例: 「認証機能の実装」「APIエラーの修正」
   - 避ける例: 「プロジェクトの作業」（具体性がない）

### 4. Markdownレポートの生成

以下のフォーマットでレポートを生成:

```markdown
# {日付} 作業レポート

## サマリー
- **セッション数**: {session_count}
- **作業時間帯**: {timeline.day_range}
- **主なタグ**: {tag_summary}
- **プロジェクト別作業時間**: {timeline.project_durations}

## タイムライン

{Claude Codeが生成するMermaid Gantt図}

## セッション一覧

### 1. [{time_range}] {project_name}

| 項目 | 内容 |
|------|------|
| **セッションID** | `{session_id}` |
| **要約** | {Claude Codeが生成した要約} |
| **タグ** | {tags} |
| **使用ツール** | {commands, subagents, skillsがあれば記載} |

**主な作業**:
- {sample_promptsから抽出した作業内容}
```

### 4.1 タイムライン生成（Claude Codeの役割）

セッション一覧の要約を生成した後、その要約を使ってMermaid Gantt図を生成する。

**生成フォーマット:**

```mermaid
gantt
    title 作業タイムライン
    dateFormat HH:mm
    axisFormat %H:%M
    todayMarker off
    section {project_name}
    {セッション要約} :{task_id}, {start_time}, {end_time}
```

**注意点:**
- Mermaid構文で問題になる文字（`;:#[]{}()`）はエスケープまたは除去する
- 要約は30文字以内に収める
- セッション一覧の要約と一致させること（整合性の担保）

### 5. レポートの保存

保存先は `config.toml` の `output_dir` を参照する。未設定の場合は `~/.claude/reports` を使用。

```
{output_dir}/{日付}.md
```

保存先ディレクトリが存在しない場合は作成すること。

## 設定ファイル

`config.toml` でカスタマイズ可能（このスキルディレクトリ内に配置）。
`config.toml.example` をコピーして作成する。各項目の詳細は README.md を参照。

## 使用例

```
/daily-report
/daily-report 2026-02-03
```
