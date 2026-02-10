# cc-daily-report

Claude Codeのセッション履歴を解析し、1日の作業内容をMarkdownレポートとして生成するスキル。

## 使い方

```
/daily-report
/daily-report 2026-02-03
```

日付を省略すると今日のレポートを生成します。

## 依存関係

- Python 3.11+（外部パッケージ不要。標準ライブラリの `tomllib` を使用）

## 設定（オプション）

設定なしでそのまま使えます。レポートは `~/.claude/reports/` に出力され、タイムゾーンはシステム設定に従います。

出力先やタグルールなどをカスタマイズしたい場合は、`config.toml.example` をコピーして編集してください。

```bash
cp config.toml.example config.toml
```

### 設定リファレンス

#### output_dir

レポートの保存先ディレクトリ。`~` はホームディレクトリに展開される。

```toml
output_dir = "~/.claude/reports"  # デフォルト
```

#### timezone

タイムスタンプの表示に使用するタイムゾーン。未設定の場合はシステムのローカルタイムゾーンを使用。

```toml
timezone = "Asia/Tokyo"
```

#### exclude_projects

レポートから除外するプロジェクト名のリスト。部分一致で判定される。

```toml
exclude_projects = [".config"]
```

#### project_aliases

プロジェクト名の表示エイリアス。ディレクトリ名の代わりにわかりやすい名前を表示する。

```toml
[project_aliases]
my-api-server = "API サーバー"
frontend-app = "フロントエンド"
```

#### tags.custom

カスタムタグのルール。`pattern` に正規表現（大文字小文字を区別しない）、`tag` にタグ名を指定する。

```toml
[[tags.custom]]
pattern = "terraform|tf"
tag = "#Terraform"

[[tags.custom]]
pattern = "docker|container"
tag = "#Docker"
```

組み込みタグ（#Python, #AWS 等）より先に評価される。

#### tags.exclude

レポートに表示しないタグのリスト。

```toml
[tags]
exclude = ["#Git", "#その他"]
```

#### output

出力に関する設定。

```toml
[output]
include_timeline = true       # Mermaid Gantt図を含めるか（デフォルト: true）
include_session_links = true  # セッションリンクを含めるか（デフォルト: true）
min_session_minutes = 1       # 最小セッション時間（分）（デフォルト: 1）
max_sample_prompts = 1        # サンプルプロンプト数（デフォルト: 1）
max_prompt_length = 150       # プロンプト最大文字数（デフォルト: 150）
max_tags_per_session = 3      # セッションあたりの最大タグ数（デフォルト: 3）
```

## ファイル構成

```
cc-daily-report/
├── SKILL.md              # スキル定義（実行手順・出力フォーマット）
├── README.md             # このファイル
├── scripts/
│   ├── parse_sessions.py # セッション履歴パーサー
│   └── config.py         # 設定読み込みモジュール
├── config.toml.example   # 設定ファイルのテンプレート
└── config.toml           # ユーザー設定（オプション）
```
