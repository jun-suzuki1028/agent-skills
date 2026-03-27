---
name: image-redactor
version: 1.0.0
description: "This skill should be used when the user asks to '画像を墨消し', 'redact image', 'アカウントIDを隠す', '画像のマスキング', '個人名を消す', 'black out sensitive info', 'スクリーンショットの墨消し', '画像から個人情報を消す', 'mask PII in screenshot', '情報を隠す', or mentions redacting, masking, or hiding AWS account IDs, personal names, IP addresses, or sensitive text from images."
---

# Image Redactor

画像内のAWSアカウントID・個人名・プロダクト名などの機密情報を検出し、黒塗りで墨消しします。

## Quick Start

```
diagrams/screenshot.png を墨消ししてください
```

```
diagrams/ フォルダ内の画像をすべて墨消し（キーワード: 鈴木, MyProduct）
```

---

## 機能概要

| 機能 | 説明 |
|------|------|
| 自動検出 | AWSアカウントID（12桁）、IPアドレス、メールアドレス、ARN |
| キーワード指定 | 個人名・プロダクト名など任意のテキストを指定して墨消し |
| 対話的確認 | 検出テキストをユーザーに提示し、追加の墨消し対象を確認 |
| 対応形式 | PNG, JPG/JPEG |
| 出力 | `_redacted` サフィックス付きの別ファイルとして保存 |

---

## 前提条件チェック

実行前に依存環境を確認する。いずれかが不足している場合はインストールコマンドを実行する。

```bash
# Tesseract OCRエンジンの確認
which tesseract || echo "MISSING: brew install tesseract tesseract-lang"

# Python依存の確認
python3 -c "import pytesseract; import PIL" 2>/dev/null || echo "MISSING: pip3 install pytesseract Pillow"
```

エラーが出た場合のインストール:
```bash
brew install tesseract tesseract-lang
pip3 install pytesseract Pillow
```

---

## 実行手順

### Phase 1: 対象の特定

ユーザーから以下を確認:
- 対象: 単一ファイル or フォルダ一括
- 追加キーワード: 墨消ししたい個人名・プロダクト名（あれば）

### Phase 2: テキスト検出（OCRスキャン）

`review` コマンドで画像をスキャンし、分類済みの結果を取得する。

**単一ファイルの場合:**
```bash
python3 .claude/skills/image-redactor/scripts/redact.py review "<image_path>"
```

**キーワード指定ありの場合:**
```bash
python3 .claude/skills/image-redactor/scripts/redact.py review "<image_path>" --keywords "鈴木" "MyProduct"
```

`review` コマンドは以下の3カテゴリに分類したJSONを返す:
- `auto_detected`: 自動検出された機密情報（AWSアカウントID、IPアドレス等）と座標
- `keyword_detected`: キーワードにマッチしたテキストと座標
- `other_texts`: 上記に該当しない一般テキスト一覧

### Phase 3: ユーザー確認

`review` の結果をユーザーに提示し、以下を確認:

1. **自動検出された項目**: 墨消しして良いか確認
2. **追加の墨消し対象**: `other_texts` 一覧から追加で墨消ししたい項目があるか
3. **キーワード追加**: 一覧にない文字列で墨消ししたいものがあるか

提示フォーマット:
```markdown
### 検出結果

**自動検出（墨消し候補）:**
- `123456789012` - AWSアカウントID
- `192.168.1.1` - IPアドレス

**キーワードマッチ:**
- `鈴木太郎` - keyword: 鈴木

**画像内のその他テキスト:**
1. `AWS Management Console`
2. `us-east-1`
3. ...

上記の中で追加で墨消ししたい項目はありますか？
番号またはキーワードで指定してください。
```

### Phase 4: 墨消し実行

ユーザーの確認後、状況に応じて適切なコマンドを選択する。

**方法A: 自動検出+キーワードで一括処理（最も一般的）:**
```bash
python3 .claude/skills/image-redactor/scripts/redact.py process "<image_path>" --keywords "鈴木" "MyProduct"
```

**方法B: キーワードなし（自動検出のみ）:**
```bash
python3 .claude/skills/image-redactor/scripts/redact.py process "<image_path>"
```

**方法C: 特定領域のみ選択的に墨消し（ユーザーが一部を除外/追加した場合）:**

`review` コマンドの出力から、ユーザーが承認した領域の座標をJSON配列で渡す:
```bash
python3 .claude/skills/image-redactor/scripts/redact.py redact "<image_path>" --regions '[{"x":10,"y":20,"w":100,"h":30},{"x":200,"y":50,"w":150,"h":25}]'
```

**フォルダ一括の場合:**
```bash
python3 .claude/skills/image-redactor/scripts/redact.py batch "<folder_path>" --keywords "鈴木" "MyProduct"
```

**出力先を指定する場合（いずれのコマンドでも使用可）:**
```bash
python3 .claude/skills/image-redactor/scripts/redact.py process "<image_path>" --output-dir "<output_dir>"
```

### Phase 5: 結果確認

1. 生成された `_redacted` ファイルをReadツールで表示し、墨消し結果をユーザーに見せる
2. 問題があれば追加のキーワードを指定して再実行

---

## コマンドリファレンス

| コマンド | 用途 | 主なオプション |
|----------|------|----------------|
| `review` | 分類済みスキャン結果を取得（対話ワークフロー用） | `--keywords`, `--lang` |
| `process` | 自動検出+キーワードで一括墨消し | `--keywords`, `--output-dir`, `--lang` |
| `redact` | 指定座標のみ選択的に墨消し | `--regions`(必須), `--output-dir` |
| `batch` | フォルダ内の画像を一括処理 | `--keywords`, `--output-dir`, `--lang` |
| `scan` | 生のOCR結果を取得（デバッグ用） | `--lang` |

---

## 出力仕様

| 項目 | 仕様 |
|------|------|
| ファイル名 | `{元のファイル名}_redacted.{拡張子}` |
| 保存先 | 元ファイルの親ディレクトリ内の `redacted/` フォルダ（output-dir未指定時） |
| 元ファイル | 変更しない |

---

## 自動検出パターン

| パターン | 例 | 説明 |
|----------|-----|------|
| AWSアカウントID | `123456789012`, `1234-5678-9012` | 12桁数字（ハイフン区切り含む） |
| AWSアクセスキーID | `AKIA1234567890ABCDEF` | AKIA/ASIAで始まる20文字 |
| AWSリソースID | `i-0abc123def`, `vpc-0abc123`, `sg-0abc123` | EC2, VPC, SG, Subnet等のリソースID |
| Organization/OU ID | `o-abc123defg`, `ou-xxxx-xxxxxxxx` | AWS Organizations関連ID |
| IPアドレス (v4) | `192.168.1.1` | IPv4アドレス |
| IPアドレス (v6) | `2001:0db8::1` | IPv6アドレス |
| メールアドレス | `user@example.com` | 標準的なメール形式 |
| ARN | `arn:aws:iam::123456789012:...` | AWSリソース識別子 |

---

## 注意事項

- OCRの精度は画像品質に依存します。小さいフォントや低解像度では検出漏れの可能性があります
- 自動検出は保守的に設定しています。必要に応じてキーワードを追加指定してください
- `_redacted` が既にファイル名に含まれるファイルはバッチ処理でスキップされます
