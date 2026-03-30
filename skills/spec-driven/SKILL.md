---
name: spec-driven
description: "プチ仕様駆動開発 - 4ドキュメント体制でタスクを管理。PLAN→SPEC→TODO→実装の流れをガイドする。「spec-driven」「仕様駆動」「4ドキュメント初期化」「spec init」で起動。"
version: "1.0.0"
user-invocable: true
---

# プチ仕様駆動開発 - 4ドキュメント駆動ワークフロー

minorun365氏の記事「[Claude Codeで「プチ仕様駆動開発」のススメ](https://qiita.com/minorun365/items/114f53def8cb0db60f47)」に基づき、プロジェクトの `tasks/` ディレクトリに4ドキュメントを初期化し、仕様駆動の開発フローをガイドする。

## Phase 1: Init — 4ドキュメント初期化

1. プロジェクトの `tasks/` ディレクトリを確認（なければ作成）
2. 以下の4ドキュメントを作成（既存の場合はスキップ）:
   - `tasks/PLAN.md` — 要件ダンプ（自由記述）
   - `tasks/SPEC.md` — 仕様の壁打ち・合意
   - `tasks/TODO.md` — タスク分解・進捗管理
   - `tasks/KNOWLEDGE.md` — 学習・ハマりポイント記録
3. テンプレートは `references/templates.md` を参照して作成する
4. 既存の `tasks/todo.md` や `tasks/lessons.md` がある場合、内容を新ドキュメントに移行する

### 初期化の実行手順

```
1. ユーザーにプロジェクトのコンテキスト（何を作るか）を確認
2. PLAN.md にユーザーの要望を記録
3. 「PLAN.mdに記録しました。SPECの壁打ちに進みますか？」と確認
```

## Phase 2: Workflow — ドキュメント駆動の進め方

### フルフロー（非自明なタスク: 3+ステップ or 設計判断あり）

```
PLAN（要件ダンプ）
  ↓ ユーザーが要望を自由に記述
SPEC（仕様の壁打ち）
  ↓ Claude が質問・整理 → ユーザーと合意
TODO（タスク分解）
  ↓ SPECからタスクを分解、チェックリスト形式
実装
  ↓ TODOに沿って進捗を更新しながら実装
KNOWLEDGE（学習記録）
  ↓ ハマりポイント・解決策を記録
```

### ライトフロー（小さなタスク: 1-2ステップ）

- `TODO.md` のみ使用でOK
- PLAN/SPECはスキップ可

### ワークフロールール

1. **SPECは合意必須**: `合意状況: [x] 合意済み` になるまで実装に進まない
2. **TODOはリアルタイム更新**: タスク完了ごとにチェックを入れる
3. **KNOWLEDGEは修正時に更新**: ユーザーから修正を受けたら必ず追記
4. **Plan modeとの併用**: SPEC合意後の実装設計にはplan modeを引き続き使用

## Phase 3: Knowledge Update — タスク完了時

タスク完了時に以下を実行:

1. `tasks/KNOWLEDGE.md` にハマりポイント・学習を追記
2. `tasks/TODO.md` の完了レビューセクションを記入
3. 次のタスクがあれば、TODO.mdを更新して継続
