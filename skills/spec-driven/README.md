# spec-driven - プチ仕様駆動開発スキル

4ドキュメント体制（PLAN / SPEC / TODO / KNOWLEDGE）でタスクを管理し、仕様駆動の開発フローをガイドするClaude Codeスキルです。

## 概要

minorun365氏の記事「[Claude Codeで「プチ仕様駆動開発」のススメ](https://qiita.com/minorun365/items/114f53def8cb0db60f47)」に基づき、以下のワークフローを実現します：

```
PLAN（要件ダンプ）→ SPEC（仕様合意）→ TODO（タスク分解）→ 実装 → KNOWLEDGE（学習記録）
```

## 使い方

1. `SKILL.md` と `references/` を `~/.claude/skills/spec-driven/` にコピー
2. Claude Codeで `/spec-driven` を実行
3. プロジェクトの `tasks/` に4ドキュメントが初期化される

## ドキュメント構成

| ドキュメント | 役割 |
|---|---|
| `tasks/PLAN.md` | 要件ダンプ（自由記述） |
| `tasks/SPEC.md` | 仕様の壁打ち・合意 |
| `tasks/TODO.md` | タスク分解・進捗管理 |
| `tasks/KNOWLEDGE.md` | 学習・ハマりポイント記録 |

## 参考

- [Claude Codeで「プチ仕様駆動開発」のススメ](https://qiita.com/minorun365/items/114f53def8cb0db60f47) by minorun365
