#!/usr/bin/env python3
"""
Claude Code セッション履歴パーサー
セッションデータを解析し、汎用的なメタデータを抽出する
具体的な要約はClaude Codeが行う
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from collections import Counter

from config import (
    load_config,
    should_exclude_project,
    should_exclude_tag,
    get_custom_tags,
)


def get_timezone(config: dict):
    """設定からタイムゾーンを取得する。未設定ならシステムのローカルTZを使用"""
    tz_name = config.get("timezone")
    if tz_name:
        try:
            from zoneinfo import ZoneInfo
            return ZoneInfo(tz_name)
        except (ImportError, KeyError):
            pass
    return None  # None = システムのローカルタイムゾーン


def parse_session_file(file_path: Path) -> dict:
    """セッションJSONLファイルをパースする"""
    data = {
        "start_time": None,
        "end_time": None,
        "cwd": "",
        "project_name": "",
        "prompts": [],
        "commands": [],       # 使用されたスラッシュコマンド
        "subagents": [],      # Task tool で起動されたサブエージェントタイプ
        "skills": [],         # Skill tool で呼び出されたスキル名
    }

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                process_record(record, data)
            except json.JSONDecodeError:
                continue

    # プロジェクト名を抽出
    if data["cwd"]:
        data["project_name"] = extract_project_name(data["cwd"])

    return data


def process_record(record: dict, data: dict):
    """レコードを処理"""
    record_type = record.get('type')
    timestamp = record.get('timestamp', '')

    if timestamp:
        if not data["start_time"] or timestamp < data["start_time"]:
            data["start_time"] = timestamp
        if not data["end_time"] or timestamp > data["end_time"]:
            data["end_time"] = timestamp

    if record.get('cwd') and not data["cwd"]:
        data["cwd"] = record['cwd']

    if record_type == 'user':
        message = record.get('message', {})
        content = message.get('content', '')
        if isinstance(content, str) and content.strip():
            # スラッシュコマンドを抽出
            cmd_match = re.search(r'<command-name>/([^<]+)</command-name>', content)
            if cmd_match:
                cmd_name = cmd_match.group(1).strip()
                if cmd_name and cmd_name not in data["commands"]:
                    data["commands"].append(cmd_name)

            cleaned = clean_prompt(content)
            if cleaned and not is_noise_prompt(content):
                data["prompts"].append(cleaned)

    elif record_type == 'assistant':
        message = record.get('message', {})
        content = message.get('content', [])
        if isinstance(content, list):
            for block in content:
                if not isinstance(block, dict) or block.get('type') != 'tool_use':
                    continue
                tool_name = block.get('name', '')
                tool_input = block.get('input', {})

                if tool_name == 'Task':
                    subagent_type = tool_input.get('subagent_type', '')
                    if subagent_type and subagent_type not in data["subagents"]:
                        data["subagents"].append(subagent_type)

                elif tool_name == 'Skill':
                    skill_name = tool_input.get('skill', '')
                    if skill_name and skill_name not in data["skills"]:
                        data["skills"].append(skill_name)


def is_noise_prompt(content: str) -> bool:
    """ノイズプロンプトを判定"""
    noise_patterns = [
        '<local-command-caveat>',
        '<local-command-stdout>',
        '<command-name>/',
        '<command-message>clear',
        '<command-message>exit',
        '<command-message>config',
        '<hook-',
        'This session is being continued',
    ]
    return any(p in content for p in noise_patterns)


def is_simple_response(content: str) -> bool:
    """単純な応答プロンプトを判定（要約生成時にスキップ）"""
    simple_patterns = [
        r'^(はい|yes|ok|うん|ええ)[、。,.\s]*$',
        r'^(進めて|お願い|続けて|続行)[ください]*[、。,.\s]*$',
        r'^(了解|わかりました|承知)[しました]*[、。,.\s]*$',
        r'^(ありがとう|thanks)[ございます]*[、。,.\s]*$',
        r'^(特になし|なし|ない|nothing)[、。,.\s]*$',
    ]
    cleaned = content.strip().lower()
    return any(re.match(p, cleaned, re.IGNORECASE) for p in simple_patterns)


def clean_prompt(content: str, max_length: int = 500) -> str:
    """プロンプトをクリーンアップ（最終的なトリミングはmainで行う）"""
    content = re.sub(r'<[^>]+>', '', content)
    content = re.sub(r'\s+', ' ', content)
    return content.strip()[:max_length]


def truncate_prompt(prompt: str, max_length: int) -> str:
    """プロンプトを指定文字数でトリミング"""
    if len(prompt) <= max_length:
        return prompt
    return prompt[:max_length - 3] + "..."


def extract_project_name(cwd: str) -> str:
    """作業ディレクトリからプロジェクト名を抽出"""
    # 一般的なパターン
    patterns = [
        r'/Documents/[^/]+/([^/]+)',  # ~/Documents/xxx/project
        r'/Projects/([^/]+)',          # ~/Projects/project
        r'/repos/([^/]+)',             # ~/repos/project
        r'/src/([^/]+)',               # ~/src/project
        r'/code/([^/]+)',              # ~/code/project
        r'\.claude/([^/]+)',           # ~/.claude/xxx
        r'/([^/]+)$',                  # 最後のディレクトリ名
    ]
    for pattern in patterns:
        match = re.search(pattern, cwd)
        if match:
            return match.group(1)
    return Path(cwd).name or "unknown"


def format_time(iso_timestamp: str, tz=None) -> str:
    """タイムスタンプを時刻形式に変換。tzが指定されていればそのTZ、なければシステムローカルTZを使用"""
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        if tz is not None:
            dt_local = dt.astimezone(tz)
        else:
            dt_local = dt.astimezone()
        return dt_local.strftime('%H:%M')
    except Exception:
        return ""


# =============================================================================
# タグ生成（汎用的な技術タグのみ）
# =============================================================================

def generate_tags(prompts: list[str], project_name: str, config: dict | None = None) -> list[str]:
    """プロンプトからタグを生成（汎用的な技術タグ）"""
    if config is None:
        config = {}

    text = ' '.join(prompts).lower()
    tags = []

    # カスタムタグを先に適用
    custom_tags = get_custom_tags(text, config)
    tags.extend(custom_tags)

    # 技術領域（汎用的）
    tech_patterns = [
        (['python', '.py', 'pytest', 'pydantic', 'pip'], '#Python'),
        (['typescript', '.ts', '.tsx', 'pnpm', 'npm', 'node'], '#TypeScript'),
        (['javascript', '.js', '.jsx'], '#JavaScript'),
        (['rust', '.rs', 'cargo'], '#Rust'),
        (['go', '.go', 'golang'], '#Go'),
        (['java', '.java', 'maven', 'gradle'], '#Java'),
        (['cdk', 'construct', 'cloudformation'], '#CDK'),
        (['terraform', '.tf', 'hcl'], '#Terraform'),
        (['docker', 'container', 'dockerfile'], '#Docker'),
        (['kubernetes', 'k8s', 'kubectl'], '#Kubernetes'),
        (['aws', 's3', 'iam', 'lambda', 'dynamodb', 'ec2'], '#AWS'),
        (['gcp', 'google cloud', 'bigquery'], '#GCP'),
        (['azure', 'microsoft cloud'], '#Azure'),
        (['git', 'commit', 'branch', 'merge', 'pr'], '#Git'),
        (['test', 'テスト', 'spec', 'jest', 'pytest'], '#Test'),
        (['doc', 'readme', 'ドキュメント', 'markdown'], '#Doc'),
    ]

    for keywords, tag in tech_patterns:
        if any(kw in text for kw in keywords):
            if tag not in tags:
                tags.append(tag)

    # 除外タグをフィルタリング
    tags = [t for t in tags if not should_exclude_tag(t, config)]

    return tags[:5]


def generate_timeline_data(sessions: list[dict], tz=None) -> dict:
    """タイムラインデータを生成（Mermaid図はClaude Codeが生成）"""
    if not sessions:
        return {"day_range": "", "project_durations": {}}

    # 時間範囲の計算
    all_starts = [s["start_time"] for s in sessions if s.get("start_time")]
    all_ends = [s["end_time"] for s in sessions if s.get("end_time")]

    if not all_starts or not all_ends:
        return {"day_range": "", "project_durations": {}}

    day_start = min(all_starts)
    day_end = max(all_ends)

    # プロジェクトごとにセッションをグループ化して合計時間を計算
    project_sessions = {}
    for s in sessions:
        proj = s.get("project_name", "unknown")
        if proj not in project_sessions:
            project_sessions[proj] = []
        project_sessions[proj].append(s)

    project_durations = {}
    for proj, proj_sessions in project_sessions.items():
        total_minutes = 0
        for s in proj_sessions:
            start = s.get("start_time")
            end = s.get("end_time")
            if start and end:
                try:
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                    total_minutes += (end_dt - start_dt).total_seconds() / 60
                except Exception:
                    pass
        project_durations[proj] = round(total_minutes / 60, 1)  # 時間単位

    return {
        "day_range": f"{format_time(day_start, tz)}-{format_time(day_end, tz)}",
        "project_durations": project_durations
    }


def get_sessions_for_date(date_str: str, projects_dir: Path) -> list[Path]:
    """指定日のセッションファイルを取得"""
    sessions = []
    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue
        for jsonl_file in project_dir.glob('*.jsonl'):
            mtime = datetime.fromtimestamp(jsonl_file.stat().st_mtime)
            if mtime.strftime('%Y-%m-%d') == date_str:
                sessions.append(jsonl_file)
    return sessions


def main():
    date_str = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime('%Y-%m-%d')
    projects_dir = Path(os.path.expanduser('~/.claude/projects'))

    # 設定を読み込む
    config = load_config()

    # タイムゾーン設定
    tz = get_timezone(config)

    session_files = get_sessions_for_date(date_str, projects_dir)

    sessions = []
    tag_counter = Counter()

    # 出力設定
    output_config = config.get("output", {})
    min_session_minutes = output_config.get("min_session_minutes", 1)
    max_sample_prompts = output_config.get("max_sample_prompts", 1)
    max_prompt_length = output_config.get("max_prompt_length", 150)
    max_tags_per_session = output_config.get("max_tags_per_session", 3)
    include_timeline = output_config.get("include_timeline", True)

    for f in sorted(session_files):
        data = parse_session_file(f)

        # 除外プロジェクトをスキップ
        if should_exclude_project(data["project_name"], config):
            continue

        if data["prompts"] or data["commands"] or data["subagents"] or data["skills"]:
            # セッション時間を計算
            duration_minutes = 0
            if data["start_time"] and data["end_time"]:
                try:
                    start_dt = datetime.fromisoformat(data["start_time"].replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(data["end_time"].replace('Z', '+00:00'))
                    duration_minutes = (end_dt - start_dt).total_seconds() / 60
                except Exception:
                    pass

            # 最小セッション時間未満はスキップ
            if duration_minutes < min_session_minutes:
                continue

            # 意味のあるプロンプトを抽出（Claude Code用）
            meaningful_prompts = [p for p in data["prompts"] if not is_simple_response(p)]

            # トークン節約: プロンプトをトリミング
            sample_prompts = [
                truncate_prompt(p, max_prompt_length)
                for p in meaningful_prompts[:max_sample_prompts]
            ]

            # タグを生成（トークン節約: 最大数を制限）
            tags = generate_tags(data["prompts"], data["project_name"], config)[:max_tags_per_session]

            # セッションIDをファイル名から取得
            session_id = f.stem

            # セッションデータを構築
            session_data = {
                "session_id": session_id,
                "start_time": data["start_time"],
                "end_time": data["end_time"],
                "project_name": data["project_name"],
                "time_range": f"{format_time(data['start_time'], tz)}-{format_time(data['end_time'], tz)}",
                # Claude Codeが要約を生成するための情報
                "commands": data["commands"],      # 使用されたスラッシュコマンド
                "subagents": data["subagents"],    # 使用されたサブエージェントタイプ
                "skills": data["skills"],          # 使用されたスキル
                "sample_prompts": sample_prompts,
                "prompt_count": len(meaningful_prompts),
                # 技術タグ
                "tags": tags,
            }

            sessions.append(session_data)
            tag_counter.update(session_data["tags"])

    sessions.sort(key=lambda s: s["start_time"] or "")

    # タグ集計
    tag_summary = dict(tag_counter.most_common(10))

    # タイムライン用データ生成（設定で無効化可能）
    timeline = generate_timeline_data(sessions, tz) if include_timeline else None

    output = {
        "date": date_str,
        "session_count": len(sessions),
        "tag_summary": tag_summary,
        "sessions": sessions
    }

    # タイムラインが有効な場合のみ追加
    if timeline:
        output["timeline"] = timeline

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
