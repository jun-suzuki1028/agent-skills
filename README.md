# cc-daily-report

Claude Codeのセッション履歴を解析し、1日の作業内容をMarkdownレポートとして生成する [Agent Skills](https://agentskills.io/) プラグイン。

## インストール

### マーケットプレイスから

```bash
/plugin marketplace add jun-suzuki1028/cc-daily-report
/plugin install cc-daily-report@cc-daily-report
```

### ローカルインストール

```bash
git clone https://github.com/jun-suzuki1028/cc-daily-report.git
/plugin install /path/to/cc-daily-report
```

## 依存関係

- Python 3.11+（外部パッケージ不要。標準ライブラリの `tomllib` を使用）

## 使い方

```
/daily-report
/daily-report 2026-02-03
```

日付を省略すると今日のレポートを生成します。

## 設定

`skills/cc-daily-report/config.toml.example` をコピーして同ディレクトリに `config.toml` を作成してください。

```bash
cp skills/cc-daily-report/config.toml.example skills/cc-daily-report/config.toml
```

### output_dir

レポートの保存先ディレクトリ。`~` はホームディレクトリに展開される。

```toml
output_dir = "~/Documents/claude-reports"  # デフォルト
```

変更すると、レポートファイル `{日付}.md` の出力先が変わる。

### timezone

タイムスタンプの表示に使用するタイムゾーン。未設定の場合はシステムのローカルタイムゾーンを使用。

```toml
timezone = "Asia/Tokyo"
```

### exclude_projects

レポートから除外するプロジェクト名のリスト。部分一致で判定される。

```toml
exclude_projects = [".config"]
```

デフォルト: `[]`（除外なし）。追加すると該当プロジェクトのセッションがレポートに表示されなくなる。

### project_aliases

プロジェクト名の表示エイリアス。ディレクトリ名の代わりにわかりやすい名前を表示する。

```toml
[project_aliases]
my-api-server = "API サーバー"
frontend-app = "フロントエンド"
```

デフォルト: `{}`（エイリアスなし）。設定するとレポート内のプロジェクト名が置き換わる。

### tags.custom

カスタムタグのルール。`pattern` に正規表現（大文字小文字を区別しない）、`tag` にタグ名を指定する。

```toml
[[tags.custom]]
pattern = "terraform|tf"
tag = "#Terraform"

[[tags.custom]]
pattern = "docker|container"
tag = "#Docker"
```

デフォルト: `[]`。追加すると、プロンプト内容がパターンにマッチした場合にそのタグが付与される。組み込みタグ（#Python, #AWS 等）より先に評価される。

### tags.exclude

レポートに表示しないタグのリスト。

```toml
[tags]
exclude = ["#Git", "#その他"]
```

デフォルト: `[]`。追加すると該当タグがセッション・サマリーの両方から除外される。

### output.include_timeline

Mermaid Gantt図（タイムライン）をレポートに含めるか。

```toml
[output]
include_timeline = true  # デフォルト
```

`false` にするとタイムラインセクションとパーサー出力の `timeline` フィールドが省略される。

### output.include_session_links

セッションリンク情報を含めるか。

```toml
[output]
include_session_links = true  # デフォルト
```

### output.min_session_minutes

レポートに含める最小セッション時間（分）。

```toml
[output]
min_session_minutes = 1  # デフォルト
```

値を大きくすると短いセッション（誤操作やちょっとした確認等）がレポートから除外される。`0` にすると全セッションを含める。

### output.max_sample_prompts

各セッションで出力するサンプルプロンプトの最大件数。

```toml
[output]
max_sample_prompts = 1  # デフォルト
```

増やすとセッションあたりのプロンプト情報が増え、要約の精度が上がるがトークン消費も増える。

### output.max_prompt_length

サンプルプロンプト1件あたりの最大文字数。超過分は `...` で切り詰められる。

```toml
[output]
max_prompt_length = 150  # デフォルト
```

増やすとプロンプトの全体像がわかりやすくなるがトークン消費が増える。

### output.max_tags_per_session

各セッションに付与するタグの最大数。

```toml
[output]
max_tags_per_session = 3  # デフォルト
```

増やすとセッションごとの技術タグが増え、サマリーのタグ集計もより詳細になる。

## ファイル構成

```
cc-daily-report/
├── .claude-plugin/
│   └── marketplace.json          # プラグインマニフェスト
├── skills/
│   └── cc-daily-report/
│       ├── SKILL.md              # スキル定義（実行手順・出力フォーマット）
│       ├── scripts/
│       │   ├── parse_sessions.py # セッション履歴パーサー
│       │   └── config.py        # 設定読み込みモジュール
│       ├── config.toml.example   # 設定ファイルのテンプレート
│       └── config.toml           # ユーザー設定（要作成・gitignore対象）
├── .gitignore
├── README.md
└── LICENSE
```

## License

MIT
