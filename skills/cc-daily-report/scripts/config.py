#!/usr/bin/env python3
"""
設定ファイル読み込みモジュール
cc-daily-report プラグインの config.toml から設定を読み込む
"""

import os
import tomllib
from pathlib import Path


DEFAULT_CONFIG = {
    # レポート保存先
    "output_dir": "~/.claude/reports",

    # 除外プロジェクト（レポートに含めない）
    "exclude_projects": [],

    # プロジェクト名のエイリアス
    "project_aliases": {},

    # タグ設定
    "tags": {
        "custom": [],
        "exclude": [],
    },

    # 出力設定
    "output": {
        "include_timeline": True,
        "include_session_links": True,
        "min_session_minutes": 1,
        # トークン節約設定
        "max_sample_prompts": 1,      # 各セッションのサンプルプロンプト数（デフォルト1件）
        "max_prompt_length": 150,     # プロンプトの最大文字数（デフォルト150文字）
        "max_tags_per_session": 3,    # 各セッションの最大タグ数
    }
}


def deep_merge(base: dict, override: dict) -> dict:
    """辞書を深くマージする"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config() -> dict:
    """設定ファイルを読み込む"""
    config_path = Path(__file__).parent.parent / "config.toml"

    if not config_path.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(config_path, 'rb') as f:
            user_config = tomllib.load(f)
        return deep_merge(DEFAULT_CONFIG, user_config)
    except Exception:
        return DEFAULT_CONFIG.copy()


def get_output_dir(config: dict) -> Path:
    """出力ディレクトリを取得"""
    output_dir = config.get("output_dir", DEFAULT_CONFIG["output_dir"])
    return Path(os.path.expanduser(output_dir))


def should_exclude_project(project_name: str, config: dict) -> bool:
    """プロジェクトを除外すべきか判定"""
    exclude_list = config.get("exclude_projects", [])
    for pattern in exclude_list:
        if pattern.lower() in project_name.lower():
            return True
    return False


def get_project_alias(project_name: str, config: dict) -> str:
    """プロジェクト名のエイリアスを取得"""
    aliases = config.get("project_aliases", {})
    return aliases.get(project_name, project_name)


def should_exclude_tag(tag: str, config: dict) -> bool:
    """タグを除外すべきか判定"""
    tags_config = config.get("tags", {})
    exclude_list = tags_config.get("exclude", [])
    return tag in exclude_list


def get_custom_tags(text: str, config: dict) -> list[str]:
    """カスタムタグを取得"""
    import re
    tags_config = config.get("tags", {})
    custom_rules = tags_config.get("custom", [])

    tags = []
    for rule in custom_rules:
        pattern = rule.get("pattern", "")
        tag = rule.get("tag", "")
        if pattern and tag and re.search(pattern, text, re.IGNORECASE):
            tags.append(tag)
    return tags
