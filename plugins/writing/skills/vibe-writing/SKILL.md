---
name: vibe-writing
description: "AI-assisted writing workflow with four phases: Learn (Socratic dialogue → knowledge cards), Structure (article framework), Write (expand and polish), Finalize (assemble full article). Use when user says '写作', '写文章', '帮我写', 'vibe', or wants to co-author any written content."
---

# Vibe Writing 写作助手

**你主导，AI辅助**。你决定写什么、怎么写，AI通过对话帮你梳理思路、组织结构。

## 四个阶段

```
学习 → 结构 → 写作 → 成稿
```

| 命令 | 阶段 | 做什么 |
|------|------|--------|
| **学习** | 默认入口 | 苏格拉底式对话，每4轮生成知识卡片 |
| **结构** | 规划框架 | 汇总卡片，提供2-3种结构方案 |
| **写作** / **迭代** | 深化润色 | 继续对话深入 → "整理"整合 → "润色"优化 |
| **成稿** | 串联输出 | 串联所有输出卡片 + 过渡段 → 完整文章 |

## 阶段1：学习

通过提问挖掘真实想法，每4轮对话整理成**知识卡片**（核心观点 + 支撑论据 + 金句）。

提问方向：
- "这个话题为什么引起你的关注？"
- "大多数人对此有什么误解？"
- "如果读者只记住一件事，你希望是什么？"

详见 [references/learning-guide.md](references/learning-guide.md)

## 阶段2：结构

汇总知识卡片 → 提供结构方案 → 拆分为输出卡片。

结构类型：问题-方案型、对比型、递进型、故事型、清单型、SCQA型。详见 [references/structure-patterns.md](references/structure-patterns.md)

## 阶段3：写作

- 说 **"整理"** → 整合对话到卡片
- 说 **"润色"** → 事实核查 + 语言优化

详见 [references/writing-guide.md](references/writing-guide.md)

## 阶段4：成稿

按顺序串联输出卡片 + 过渡段落 + 开头结尾 → 完整文章。

## 灵活使用

| 场景 | 从哪开始 |
|------|----------|
| 从零写 | 完整四阶段 |
| 已有想法 | 直接说"结构" |
| 已有初稿 | 直接说"迭代" |
| 头脑风暴 | 只用学习阶段 |

## 参考资料

- [卡片模板](references/card-templates.md)
- [结构模式](references/structure-patterns.md)
- [学习指南](references/learning-guide.md)
- [写作指南](references/writing-guide.md)
