#!/usr/bin/env python3
"""知识库管理脚本 - 用于添加新知识条目到知识库中"""

import os
import sys
from datetime import datetime

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "..", "references", "knowledge")

CATEGORIES = {
    "restaurant": "restaurants.md",
    "hotel": "hotels.md",
    "activity": "activities.md",
    "transport": "transport.md",
    "seasonal": "seasonal.md",
    "budget": "budget_guide.md",
}

ENTRY_TEMPLATE = """
## {name}
- **日期**：{date}
- **来源**：{source}
- **区域**：{area}
- **标签**：{tags}

{content}
"""

def add_entry(category, name, content, area="", tags="", source="用户反馈"):
    """添加一条新知识"""
    if category not in CATEGORIES:
        print(f"❌ 未知分类: {category}")
        print(f"   可用分类: {', '.join(CATEGORIES.keys())}")
        return False

    filename = os.path.join(KNOWLEDGE_DIR, CATEGORIES[category])
    date = datetime.now().strftime("%Y-%m-%d")

    entry = ENTRY_TEMPLATE.format(
        name=name,
        date=date,
        source=source,
        area=area or "待补充",
        tags=tags or "待分类",
        content=content,
    )

    with open(filename, "a", encoding="utf-8") as f:
        f.write(entry)

    print(f"✅ 已添加到 {CATEGORIES[category]}: {name}")
    return True


def update_index():
    """更新知识库索引"""
    index_path = os.path.join(KNOWLEDGE_DIR, "INDEX.md")
    counts = {}

    for cat, filename in CATEGORIES.items():
        filepath = os.path.join(KNOWLEDGE_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            counts[cat] = content.count("\n## ")  # 计数二级标题

    # 重建索引
    lines = [
        "# 知识库索引",
        "",
        f"> 自动生成 | 最后更新：{datetime.now().strftime('%Y-%m-%d')}",
        "> ",
        "> 本索引记录所有自学习的知识条目。每新增一条知识，在此追加记录。",
        "",
        "## 📊 统计",
        "",
        "| 分类 | 条目数 |",
        "|------|--------|",
    ]
    for cat, count in counts.items():
        lines.append(f"| {cat} | {count} |")
    lines += [
        "",
        "## 📝 条目列表",
        "",
        "_（使用后自动填充）_",
    ]

    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ 索引已更新")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法: python knowledge.py <分类> <名称> <内容> [区域] [标签]")
        print(f"分类: {', '.join(CATEGORIES.keys())}")
        sys.exit(1)

    cat, name, content = sys.argv[1], sys.argv[2], sys.argv[3]
    area = sys.argv[4] if len(sys.argv) > 4 else ""
    tags = sys.argv[5] if len(sys.argv) > 5 else ""

    if add_entry(cat, name, content, area, tags):
        update_index()
