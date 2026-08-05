#!/usr/bin/env python3
"""
耄耋随机关心脚本（通用版）
========================
功能：读取今天和昨天的记忆会话，提取未完成事项，作为关心消息的上下文。
完全通用，不包含任何个人隐私信息。

使用方法：
1. 确保已加载 maodie 技能
2. 设置 cronjob（二选一）：

   方式 A — 通过 Hermes 工具设置：
   cronjob(
     action='create',
     name='maodie-checkin',
     schedule='*/12 * * * *',
     script='maodie/cron/checkin_script.py',
     prompt='根据下面提供的记忆内容，判断用户有没有什么未完成的事情或需要关心的地方，然后发一条简短关心的消息到当前对话。如果记忆内容为空，就发一条普通的问候。',
     skills=['maodie'],
     enabled_toolsets=['file']
   )

   方式 B — 通过 CLI 设置：
   hermes cron add --name maodie-checkin --schedule "*/12 * * * *" \
     --script maodie/cron/checkin_script.py \
     --prompt "根据下面提供的记忆内容，判断用户有没有什么未完成的事情或需要关心的地方，然后发一条简短关心的消息到当前对话。如果记忆内容为空，就发一条普通的问候。" \
     --skills maodie \
     --enabled-toolsets file

注意：
- 脚本每12分钟触发一次，每次约2%概率真正发消息
- 一天最多发1-2条
- 如果最近12分钟内用户发过消息，会自动跳过
- 电脑关机时自动停止，开机后自动恢复
"""

import os, json, random, datetime
from pathlib import Path

# 概率控制（可调）
TRIGGER_PROBABILITY = 0.30  # 30% 概率触发
COOLDOWN_MINUTES = 12       # 最近12分钟有消息则跳过

def get_skill_dir():
    """获取 maodie 技能目录路径"""
    # 尝试从环境变量或默认路径获取
    home = os.path.expanduser("~")
    candidates = [
        os.path.join(home, "AppData", "Local", "hermes", "skills", "leisure", "maodie"),
        os.path.join(home, ".hermes", "skills", "leisure", "maodie"),
        os.path.join(home, "hermes", "skills", "leisure", "maodie"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return candidates[0]

def get_session_file(skill_dir, date_str):
    """获取指定日期的会话文件路径"""
    return os.path.join(skill_dir, "memory", "sessions", f"{date_str}.md")

def get_today_yesterday():
    """获取今天和昨天的日期字符串"""
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    return today.strftime("%Y-%m-%d"), yesterday.strftime("%Y-%m-%d")

def read_session(filepath):
    """读取会话文件内容"""
    if not os.path.exists(filepath):
        return ""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

def extract_unresolved_topics(content):
    """从会话内容中提取未完成事项的线索"""
    if not content:
        return []
    
    lines = content.split("\n")
    topics = []
    keywords = {
        "未写完": "未完成",
        "未完成": "未完成",
        "明天": "待办",
        "下周": "待办",
        "还没": "未完成",
        "还没想好": "未决定",
        "不知道": "困惑",
        "怎么办": "求助",
        "要改": "待办",
        "要调整": "待办",
        "要加班": "工作",
        "要去": "计划",
        "想见": "愿望",
        "放不下": "情感",
        "后悔": "情感",
        "犹豫": "犹豫",
    }
    
    for line in lines:
        for keyword, category in keywords.items():
            if keyword in line:
                topics.append({"keyword": keyword, "category": category, "line": line.strip()})
                break
    
    return topics

def main():
    skill_dir = get_skill_dir()
    today_str, yesterday_str = get_today_yesterday()
    
    # 读取会话文件
    today_content = read_session(get_session_file(skill_dir, today_str))
    yesterday_content = read_session(get_session_file(skill_dir, yesterday_str))
    
    # 提取未完成事项
    today_topics = extract_unresolved_topics(today_content)
    yesterday_topics = extract_unresolved_topics(yesterday_content)
    
    # 输出结构化数据给 agent 使用
    output = {
        "today": today_str,
        "yesterday": yesterday_str,
        "has_today_session": bool(today_content),
        "has_yesterday_session": bool(yesterday_content),
        "today_session_length": len(today_content),
        "yesterday_session_length": len(yesterday_content),
        "unresolved_topics": {
            "today": [t["category"] for t in today_topics[:3]],
            "yesterday": [t["category"] for t in yesterday_topics[:3]],
        },
        "has_unresolved": bool(today_topics or yesterday_topics),
        "summary": "",
    }
    
    # 生成简短摘要
    if today_topics:
        categories = set(t["category"] for t in today_topics[:3])
        output["summary"] = f"今天有未完成事项，涉及{'、'.join(categories)}。"
    elif yesterday_topics:
        categories = set(t["category"] for t in yesterday_topics[:3])
        output["summary"] = f"昨天有未完成事项，涉及{'、'.join(categories)}。"
    else:
        output["summary"] = "近两天无明显未完成事项。"
    
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()