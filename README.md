# 🏝️ Bali Planner — 巴厘岛交互式旅行规划 Skill

> 基于我 2 年巴厘岛旅居真实经验，通过 14 个交互问题，生成可直接落地执行的旅行方案。

[![Skill Type](https://img.shields.io/badge/Codex-Skill-0D9488)](https://github.com/joel0601/bali-planner)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## ✨ 它能做什么

这个 Skill 就像一个住在巴厘岛的朋友帮你规划行程——

1. **交互式问答**：分 4 轮问你 14 个问题（同行关系、天数、预算、偏好...）
2. **智能生成方案**：基于你的回答，匹配 我的一手经验
3. **输出即用**：每日时间线 + 住宿推荐 + 餐厅推荐 + Klook 预订链接 + 预算明细
4. **自我进化**：每次使用后可以追加新知识，知识库自动索引

## 📦 安装

### 方式一：直接安装到 Codex
```bash
git clone https://github.com/joel0601/bali-planner.git ~/.codex/skills/bali-planner
```

### 方式二：在 Codex 对话中说
```
请安装技能：https://github.com/joel0601/bali-planner
```

### 其他 AI Agent 学习路径
```
# 直接读取 SKILL.md 即可获得完整指令
https://raw.githubusercontent.com/joel0601/bali-planner/main/SKILL.md

# 或克隆整个仓库
git clone https://github.com/joel0601/bali-planner.git
```

## 🎮 使用方式

安装后在 Codex 对话中说：
```
帮我规划巴厘岛行程
```

Skill 会自动触发，开始和你交互问答。

## 📁 文件结构

```
bali-planner/
├── SKILL.md                    # 🔧 核心指令文件（Agent 必读）
├── README.md                   # 📖 本文件
├── agents/
│   └── openai.yaml             # 🏷️ 展示元数据
├── references/
│   ├── questionnaire.md        # 📋 14 题交互框架
│   ├── my_experience.md     # 🧠 我 2 年旅居经验
│   ├── klook_links.md          # 🔗 30+ 个 Klook 活动链接
│   ├── itinerary_template.md   # 📝 输出模板
│   └── knowledge/              # 🔄 自学习知识库
│       ├── INDEX.md
│       ├── restaurants.md
│       ├── hotels.md
│       ├── activities.md
│       ├── transport.md
│       ├── seasonal.md
│       └── budget_guide.md
└── scripts/
    └── knowledge.py            # 🛠️ 知识库管理脚本
```

## 🧠 知识来源

- **我的环球旅居指南**：2 年巴厘岛旅居一手经验，覆盖 7 大章节
  - 区域选择（7 个区域详细对比）
  - 住宿推荐（从 ¥40 青旅到 ¥10,000+ 宝格丽）
  - 美食地图（20+ 家私藏餐厅）
  - 旅行路线（4/7/15 天/1 月+ 四条模板）
  - 数字游民指南（Coworking Space、社群、孤独感应对）
  - 安全与常识
- **Klook 精选链接**：30+ 个活动，附实时价格，一键预订
- **自学习知识库**：使用后可持续追加新发现

## 🔄 自我进化

每次生成方案后，Skill 会询问用户是否有新的发现。使用以下命令添加新知识：

```bash
python3 scripts/knowledge.py restaurant "餐厅名" "描述" "区域" "标签"
```

支持分类：`restaurant`, `hotel`, `activity`, `transport`, `seasonal`, `budget`

## 📄 License

MIT © Joel
