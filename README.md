# cc-plugins

Claude Code用のプラグインマーケットプレイスです。各プラグインを個別にインストールできます。

## インストール

### 1. マーケットプレイスを追加

```
/plugin marketplace add jun-suzuki1028/cc-plugins
```

### 2. プラグインを選んでインストール

```
/plugin install cc-bestpractice-check@jun-suzuki1028-cc-plugins
/plugin install image-redactor@jun-suzuki1028-cc-plugins
/plugin install spec-driven@jun-suzuki1028-cc-plugins
```

### ローカルから導入（開発用）

```
claude --plugin-dir ./plugins/cc-bestpractice-check
claude --plugin-dir ./plugins/image-redactor
claude --plugin-dir ./plugins/spec-driven
```

### インタラクティブUI

`/plugin` を実行すると対話的にプラグインを管理できます。

## プラグイン一覧

| プラグイン | 説明 |
|-----------|------|
| [cc-bestpractice-check](plugins/cc-bestpractice-check/) | Claude Code設定をベストプラクティスと比較しギャップをレポート |
| [image-redactor](plugins/image-redactor/) | 画像内の機密情報をOCRで検出し墨消し |
| [spec-driven](plugins/spec-driven/) | プチ仕様駆動開発 - 4ドキュメント体制でPLAN→SPEC→TODO→実装をガイド |
