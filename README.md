# agent-skills

Claude Code用のスキルコレクションプラグインです。

## インストール

### GitHub から導入

1. マーケットプレイスを追加

```
/plugin marketplace add jun-suzuki1028/agent-skills
```

2. プラグインをインストール

```
/plugin install agent-skills@jun-suzuki1028-agent-skills
```

### ローカルから導入

```
claude --plugin-dir /path/to/agent-skills
```

### インタラクティブUI

`/plugin` を実行すると対話的にプラグインを管理できます。

## インストール後

プラグインを有効化した後、変更を反映するには以下を実行します。

```
/reload-plugins
```

## スキル一覧

| スキル | 説明 |
|--------|------|
| [cc-bestpractice-check](skills/cc-bestpractice-check/) | Claude Code設定をベストプラクティスと比較しギャップをレポート |
| [image-redactor](skills/image-redactor/) | 画像内の機密情報をOCRで検出し墨消し |
| [spec-driven](skills/spec-driven/) | プチ仕様駆動開発 - 4ドキュメント体制でPLAN→SPEC→TODO→実装をガイド |
