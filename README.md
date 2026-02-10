# claude-skills

Claude Code向けスキルコレクション。[Agent Skills](https://agentskills.io/) 仕様に準拠。

## インストール

### マーケットプレイスから

```bash
/plugin marketplace add jun-suzuki1028/claude-skills
```

利用可能なプラグイン一覧から選んでインストール:

```bash
/plugin install cc-daily-report@claude-skills
```

### ローカルインストール

```bash
git clone https://github.com/jun-suzuki1028/claude-skills.git
/plugin install /path/to/claude-skills
```

## スキル一覧

### cc-daily-report

Claude Codeのセッション履歴を解析し、1日の作業内容をMarkdownレポートとして生成する。

```
/daily-report
/daily-report 2026-02-03
```

**依存関係:** Python 3.11+（外部パッケージ不要）

**設定:** `skills/cc-daily-report/config.toml.example` をコピーして `config.toml` を作成。

```bash
cp skills/cc-daily-report/config.toml.example skills/cc-daily-report/config.toml
```

詳細は [skills/cc-daily-report/](skills/cc-daily-report/) を参照。

## 設定リファレンス

### cc-daily-report

| 設定項目 | デフォルト | 説明 |
|----------|-----------|------|
| `output_dir` | `~/.claude/reports` | レポート保存先 |
| `timezone` | システムTZ | タイムゾーン（例: `Asia/Tokyo`） |
| `exclude_projects` | `[]` | 除外プロジェクト（部分一致） |
| `project_aliases` | `{}` | プロジェクト名エイリアス |
| `tags.custom` | `[]` | カスタムタグルール |
| `tags.exclude` | `[]` | 除外タグ |
| `output.include_timeline` | `true` | Mermaid Gantt図を含めるか |
| `output.min_session_minutes` | `1` | 最小セッション時間（分） |
| `output.max_sample_prompts` | `1` | サンプルプロンプト数 |
| `output.max_prompt_length` | `150` | プロンプト最大文字数 |
| `output.max_tags_per_session` | `3` | セッションあたりの最大タグ数 |

## ファイル構成

```
claude-skills/
├── .claude-plugin/
│   └── marketplace.json
├── skills/
│   └── cc-daily-report/
│       ├── SKILL.md
│       ├── scripts/
│       │   ├── parse_sessions.py
│       │   └── config.py
│       └── config.toml.example
├── .gitignore
├── README.md
└── LICENSE
```

## License

MIT
