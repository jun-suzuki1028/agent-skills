# image-redactor

画像内のAWSアカウントID・個人名・プロダクト名などの機密情報をOCRで検出し、黒塗りで墨消しするスキル。

## 使い方

```
img/screenshot.png を墨消ししてください
```

```
img/ フォルダ内の画像をすべて墨消し（キーワード: 鈴木, MyProduct）
```

画像パスを渡すだけで、自動検出→ユーザー確認→墨消し実行の対話的ワークフローが走ります。

## 依存関係

- Python 3.11+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)（`brew install tesseract tesseract-lang`）
- [pytesseract](https://pypi.org/project/pytesseract/)（`pip3 install pytesseract`）
- [Pillow](https://pillow.readthedocs.io/)（`pip3 install Pillow`）

## 自動検出パターン

| パターン | 例 | 説明 |
|----------|-----|------|
| AWS アカウント ID | `123456789012`, `1234-5678-9012` | 12桁数字（ハイフン区切り含む） |
| AWS アクセスキー ID | `AKIA1234567890ABCDEF` | AKIA/ASIAで始まる20文字 |
| AWS リソース ID | `i-0abc123def`, `vpc-0abc123`, `sg-0abc123` | EC2, VPC, SG, Subnet等のリソースID |
| Organization / OU ID | `o-abc123defg`, `ou-xxxx-xxxxxxxx` | AWS Organizations関連ID |
| IP アドレス (v4/v6) | `192.168.1.1`, `2001:0db8::1` | IPv4 / IPv6アドレス |
| メールアドレス | `user@example.com` | 標準的なメール形式 |
| ARN | `arn:aws:iam::123456789012:...` | AWSリソース識別子 |

## スキル発動トリガー

以下のフレーズでスキルが自動的に発動します。

| 言語 | トリガー例 |
|------|-----------|
| 日本語 | 画像を墨消し、アカウントIDを隠す、画像のマスキング、個人名を消す、スクリーンショットの墨消し |
| English | redact image, black out sensitive info, mask PII in screenshot |

## ファイル構成

```
image-redactor/
├── SKILL.md              # スキル定義（実行手順・コマンドリファレンス）
├── README.md             # このファイル
└── scripts/
    └── redact.py         # OCR検出・墨消し処理スクリプト
```
