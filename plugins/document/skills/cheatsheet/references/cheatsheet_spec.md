# Cheatsheet Markdown Spec

Markdown → HTML cheatsheet 转换规范。
转换工具：`python3 md2html.py input.md -o output.html`

## 输出格式

- A4 横向 (297mm × 210mm)，每页 5 列
- 字体 6pt，行高 1.22，紧凑排版，适合打印
- `column-fill: auto`：内容从左到右、从上到下依次排列
- `---PAGE---` 分隔多页，每页对应一张 A4
- 不使用 `---PAGE---` 时所有内容在一页（溢出部分被隐藏）

## 文档结构

```
---
title: 标题
subtitle: 副标题（可留空）
---

# 章节标题          ← 蓝色横幅（section header）

## 小节标题          ← 红色行内标题（subsection header）
正文内容...         ← 第一段与 ## 标题同行显示

更多正文...         ← 空行分隔 = 新段落

## 另一个小节
...

---PAGE---          ← 分页符

# 第二页章节
...
```

## Front Matter

文件开头用 `---` 包裹的 YAML 元数据：

```
---
title: 70016 NLP Cheat Sheet
subtitle:
---
```

- `title`: HTML `<title>` 标签内容
- `subtitle`: 目前未显示（页面标题已移除以节省空间）

## 块级语法

| 语法 | 说明 | HTML 输出 |
|------|------|-----------|
| `# 标题` | 章节标题 | `<div class="s">` 蓝色横幅 |
| `## 标题` | 小节标题 | `<span class="h">` 红色粗体，与首段同行 |
| `---PAGE---` | 分页符 | 新的 `<div class="page">` |
| `> 文本` | 备注框 | `<div class="note">` 绿色左边框 |
| `| a | b |` | 表格 | `<table>` 蓝色表头 |
| 空行 | 段落分隔 | 新 `<p>` 标签 |

### 段落规则

- `##` 之后的**第一段**与标题同行显示（标题后接空格再接正文）
- 后续段落各自独立 `<p>`
- 同一段内的多行文本会被合并（join by space）

### Break-Avoid 行为

- 所有带标题的 `##` 块都会被包裹在 `<div class="break-avoid">` 中
- 这意味着整个 `##` 块（标题+所有段落+表格）不会在列中间断开
- 如果一个块放不下当前列的剩余空间，会跳到下一列顶部
- ⚠️ 这会在列底部产生空白间隙——这是正常的，用于确保内容块的完整性
- **较小的 `##` 块**（1-2 段）产生的间隙更小，排版更紧凑
- **较大的 `##` 块**（多段+表格）可能产生较大间隙

### 表格

```
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 数据 | 数据 | 数据 |
```

- 第二行全为 `-`（可含 `:`）= 表头分隔行
- 表头行：蓝色背景
- ⚠️ 公式中的 `|` 会被误解析为列分隔符，用 `‖` 或 `·` 替代

### 备注框

```
> 这是一条绿色备注
> 可以跨多行（会合并为一行）
```

## 行内语法

| 语法 | 效果 | HTML |
|------|------|------|
| `**粗体**` | **粗体** | `<b>` |
| `$公式$` | 蓝色斜体 | `<span class="m">` |
| `$=关键公式=$` | 黄底蓝色斜体 | `<span class="k"><span class="m">` |
| `==关键文本==` | 黄底高亮 | `<span class="k">` |
| `@@行内标题@@` | 红色粗体标题 | `<span class="h">` |
| `^{上标}` | 上标 | `<sup>` |
| `_{下标}` | 下标 | `<sub>` |
| `~{灰色文本}~` | 灰色小字 | `<span class="g">` |

### 行内语法示例

```markdown
## Activations
**Sigmoid**: $σ(x)=1/(1+e^{−x})$ ∈(0,1). **ReLU**: $max(0,x)$.

## Lemma vs Stem
Lemma→valid word. @@Tokenisation@@ Split text→tokens.

$=h = g(xW + b)=$  ← 关键公式（黄底）

==must memorize==  ← 关键文本（黄底）
```

## 排版指南

### 内容密度
- 6pt 字体，尽量压缩文本，用缩写和符号
- 每页 5 列 × ~80 行 ≈ 400 行文本容量
- Unicode 符号：→, ≈, ∈, ⊙, Σ, Π, ∂, ≤, ≥, ², ³ 等

### 填充策略
- `column-fill: auto` 从左到右依次排列，每列排满再到下一列
- 内容不够 5 列 → 右侧列为空 → 需要添加更多内容
- 内容过多 → 溢出被隐藏 → 需要减少内容或添加 `---PAGE---`
- 目标：每页的 5 列都填满（最后一列可以稍短）

### 块大小建议
- `##` 块尽量保持 1-3 段，避免过大的块（>10 行）产生大的列底间隙
- 用 `@@子标题@@` 在同一 `##` 块内添加子标题，不会创建新的 break-avoid 块
- 表格尽量控制在 5-8 行以内
- 如需大段内容，拆分成多个独立的 `##` 块

### 分页
- 不使用 `---PAGE---`：所有内容在一页
- 推荐做法：先不分页，确认总内容量刚好够 N 页后，再在合适位置插入 `---PAGE---`

## 完整示例

```markdown
---
title: My Cheat Sheet
subtitle:
---

# Ch1: Topic Name

## Core Concept
**Definition**: explanation here. $=key_formula=$. More text with $math$ inline.

## Comparison
| A | B | C |
|---|---|---|
| x | y | z |

## Details
First paragraph joined with title. ==highlight this==.

Second paragraph is separate. ^{superscript} and _{subscript}.

@@Sub-topic@@ More content under a red sub-header within the same block.

> Important note in green box

---PAGE---

# Ch2: Another Topic
...
```

## 构建命令

```bash
python3 md2html.py input.md -o output.html
```

打印设置：A4 横向，边距=无，启用背景图形。

## 文件清单

| 文件 | 说明 |
|------|------|
| `md2html.py` | Markdown→HTML 转换脚本（独立运行，无依赖） |
| `CHEATSHEET_SPEC.md` | 本文档，语法和排版规范 |
| `*.md` | 源内容文件 |
| `*.html` | 生成的 cheatsheet（用浏览器打开 / Ctrl+P 打印） |
