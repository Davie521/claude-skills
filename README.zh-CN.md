# Claude Skills

[English](README.md) | **中文**

Yifan 个人 Claude Code 插件市场 — **15 个 plugin / 52 个 skill + 5 个 review agent + 1 个 review 命令**，覆盖开发工作流、设计、语言模式、测试、研究等。

## Plugin 总览

| Plugin | Skill 数 | 用途 |
|--------|---------|------|
| [`dev-workflow`](#dev-workflow) | 10 | Git PR 自动化（含自动合并）、深度规划、**拷问、调试纪律、架构深化、issue triage** |
| [`document`](#document) | 4 | A4 速查表、文档协作、PDF、签证文档翻译 |
| [`work-tools`](#work-tools) | 1 | 飞书集成 |
| [`writing`](#writing) | 3 | Vibe 写作（含声音捕捉）、多平台分发、视频编辑 |
| [`design`](#design) | 3 | UI/UX Pro Max、UX critique、codebase-to-course |
| [`swift`](#swift) | 4 | Swift/iOS：SwiftUI + 架构模式、并发、Liquid Glass、端上 LLM |
| [`web`](#web) | 6 | REST API、MCP server、Docker、部署、Bun、内容哈希缓存 |
| [`data`](#data) | 3 | PostgreSQL、迁移、自动爬虫 |
| [`quality`](#quality) | 8 | TDD、E2E、安全审查/扫描、对抗式验证 |
| [`code-review`](#code-review) | 5 agent + 1 命令 | `/code-review` 自动按语言分发到 Python/TypeScript/Swift 专家 + 强制 security 审查 |
| [`research`](#research) | 4 | 深度研究（含市场调研）、搜索路由、成本感知 LLM 管道 |
| [`skills`](#skills) | 3 | Skill 管理 — 盘点、合规审计、规则蒸馏 |
| [`business`](#business) | 1 | 投资人材料 + outreach 跟进节奏 |
| [`codex`](#codex) | 2 | Codex MCP 第二意见 — 代码审查、方案质疑 |
| [`session-summary`](#session-summary) | 仅 hooks | 会话总结 hooks 和脚本（无 skill） |

---

## dev-workflow

自动化开发工作流。

#### `/cpr` — Git PR 流水线

一条命令从本地改动到合并完成。原 Copilot Lint 审查工作流已并入 — 说 `cl` 仍能触发。Claude 自动完成：

1. 检测当前 git 状态（未提交更改、已有 PR、CI 状态）
2. 提交并推送代码，通过 `gh` 创建 PR
3. 用 `gh pr checks --watch` 监听 CI
4. CI 失败：读取错误日志 → 修复代码 → 重新推送
5. CI 通过：拉取 PR 上的 Copilot 审查评论
6. 按「必须修 / 可忽略」判断表评估每条评论 — 只修真正的 bug 和安全问题，忽略过度防御、误报、纯风格偏好
7. 循环步骤 3–6 直到全部通过
8. CI 全绿后自动合并 — 如有 review 未通过则暂停合并并通知你

#### 其他 dev-workflow skills

- **`grill-with-docs`** — 让 Claude **反过来无情拷问你**的 plan，一次一个问题，对照项目领域模型逼问，**实时更新** `CONTEXT.md`（领域术语表）和 `docs/adr/`（按内置 `ADR-FORMAT.md` 的结构），是 CONTEXT.md 文化的生产者。没有 `CONTEXT.md` 时降级为轻量模式：只拷问，不写文档。说 "grill me" 仍能触发
- **`diagnose`** — 6 阶段调试纪律（构造反馈回路 → 复现 → 列 3-5 个排序假设 → 用 `[DEBUG-xxxx]` 唯一前缀打探针 → 修复+回归测试 → 清理 grep）针对疑难 bug 和性能回归
- **`improve-codebase-architecture`** — 找架构深化机会（强制使用 Module / Interface / Depth / Seam 术语 + "deletion test" 启发式），列候选 → 用户挑一个 → drop into 拷问
- **`prototype`** — 抛弃式原型，强制二分支决策：逻辑/状态问题 → 终端交互 TUI；UI 问题 → 同路由多变体切换栏
- **`to-prd`** — 把当前会话直接合成成 PRD（**不再 interview**），发到 GitHub issue 或存到 `docs/prds/`
- **`triage`** — Issue 5 状态机（needs-triage / needs-info / ready-for-agent / ready-for-human / wontfix），自带 `.out-of-scope/` 拒绝知识库
- **`caveman`** — 持续压缩 ~75% token 的回复模式，删冠词/客套话但保留所有技术内容
- **`deep-plan`** — 复述需求 → 评估风险 → 分阶段计划 → **等明确确认**；批准后第一步强制建隔离 git worktree，实现完交接 `/cpr` 或 code review
- **`cleanup`** — 会话收尾：关掉本次启动的所有进程、按 diff 同步过时文档、残留任务清零（做完或明确报告）、经验沉淀进记忆 — Phase 4 从会话抽可复用模式、自评并决定保存范围；每个 Phase 必须给出带证据的「已处理/无需处理」结论

---

## document

#### `cheatsheet` — A4 速查表生成器

从 Markdown 生成高密度、可打印的速查表：

- **A4 横版**，5 栏布局，6pt 字体
- 支持 LaTeX 数学公式、表格、高亮块、注释
- 多页输出。流程：Markdown → `python3 md2html.py input.md` → HTML → PDF

#### 其他 document skills

- **`doc-coauthoring`** — 结构化协作写技术文档 / 提案 / 决策文档
- **`pdf`** — PDF 提取 / 生成 / 表单 / OCR
- **`visa-doc-translate`** — 签证文档（图片）翻译为中英双语 PDF

---

## work-tools

#### `feishu` — 飞书集成

通过 MCP server 操作飞书：

- 发消息给用户或群组
- 建群聊
- 建/编辑文档
- 上传文件
- 查询用户信息

需要配置飞书 MCP server。

---

## writing

#### `vibe-writing` — AI 写作助手

4 阶段协作写作流程：

| 阶段 | 触发词 | 做什么 |
|------|--------|--------|
| **学习** | 默认 | 苏格拉底式对话，每 4 轮生成知识卡片 |
| **结构** | "结构" | 提供 2–3 种文章结构（问题-方案 / 对比 / 递进 / 故事 / 清单 / SCQA） |
| **写作** | "写作" / "迭代" | "整理"整合，"润色"事实核查 + 语言优化 |
| **成稿** | "成稿" | 串联输出卡片 + 过渡段落 + 开头结尾 |

同时负责长文的声音一致性：五维声音捕捉清单 + AI 腔禁用词表。

#### 其他 writing skills

- **`crosspost`** — 多平台分发，按平台适配（不复制粘贴），带三平台各自的要点清单 + 一份素材的 repurposing cascade。只起草，不发布
- **`video-editing`** — AI 辅助视频剪辑（FFmpeg / Remotion / ElevenLabs / fal.ai）

---

## design

三个 skill。反 AI 味的纪律交给 [Hallmark](https://github.com/Nutlope/hallmark)，
可测量的无障碍/性能审计交给 `chrome-devtools` MCP 的 `lighthouse_audit`。
这个插件只覆盖那两者都不做的部分。

- **`ui-ux-pro-max`** — 设计智能库：67 风格 / 96 配色 / 57 字体搭配 / 13 技术栈，
  可搜索数据库。产出 `design-system/MASTER.md` 以及项目根的 `design.md` 指针，
  让 Hallmark 识别为"系统托管"项目。
  官方设计系统路由表见 `reference/design-system-map.md`
  （Fluent / Material 3 / Carbon / Polaris / Atlaskit / Primer / govuk-frontend / USWDS）。
- **`critique`** — UX 体验评估：认知负荷、情绪旅程（峰终定律）、视觉层级、
  可发现性、persona 红旗。10 个维度 + 评分体系 + 5 个用户原型。
  回答"这个体验成不成立"，而不是"看起来像不像 AI 做的"。
- **`codebase-to-course`** — 把代码库变成交互式 HTML 教程。

那 20 个单动词 skill（`bolder` / `quieter` / `distill` / `audit` …）已于
2026-08-08 移除：零调用，且它们的调度入口依赖一个被禁用的 `frontend-design`。

---

## swift

Swift 和 iOS 开发：

- **`swiftui-patterns`** — SwiftUI 架构、`@Observable`、导航、性能；新增 Architecture Patterns 区（actor 线程安全持久化、基于协议的依赖注入测试）
- **`swift-concurrency-6-2`** — Swift 6.2 Approachable Concurrency、`@concurrent`、isolated conformances
- **`liquid-glass-design`** — iOS 26 Liquid Glass 材质（模糊、反射、形变）
- **`foundation-models-on-device`** — Apple FoundationModels 端上 LLM（`@Generable`、工具调用、流式）

---

## web

TypeScript / Node Web 全栈：

- **`bun-runtime`** — Bun 作为运行时 / 包管理 / 打包 / 测试
- **`api-design`** — REST API 模式（资源命名、状态码、分页、错误、版本）
- **`mcp-server-patterns`** — TS SDK 写 MCP server（tools、resources、Zod、stdio vs HTTP）
- **`docker-patterns`** — Docker + Compose 本地开发、安全、网络
- **`deployment-patterns`** — CI/CD、容器化、健康检查、回滚
- **`content-hash-cache-pattern`** — SHA-256 内容哈希缓存

---

## data

数据工程：

- **`postgres-patterns`** — 查询优化、schema 设计、索引、安全
- **`database-migrations`** — 零停机 schema 变更（PostgreSQL / MySQL / Prisma / Drizzle / Django）
- **`data-scraper-agent`** — 100% 免费 GitHub Actions 数据采集 agent（Gemini Flash + Notion/Sheets/Supabase）

---

## quality

代码质量、测试、审查：

**测试（4）：**
- **`tdd-workflow`** — TDD 80%+ 覆盖率（单元 + 集成 + E2E）
- **`e2e-testing`** — Page Object Model、CI/CD 集成、flaky 测试策略
- **`click-path-audit`** — 追踪每个按钮的状态变化（找 UI 不一致）
- **`ai-regression-testing`** — 抓 AI 自审盲点（同一模型既写又审）

**审查（4）：**
- **`security-review`** — 完整安全审查清单（认证 / 输入 / 密钥 / API）
- **`security-scan`** — 扫描 `.claude/` 配置漏洞（CLAUDE.md / settings / hooks / agents）
- **`plankton-code-quality`** — 写时自动 format/lint/fix（每次编辑触发）
- **`santa-method`** — 多 agent 对抗式验证（两个独立 reviewer 都通过才 ship）

---

## code-review

多语言 code review 自动分发。一条命令（`/code-review`）检测变更涉及的语言，并行调起对应的语言专家 agent，外加每次必跑的 security 审查。

**命令：**
- **`/code-review`** — 本地未提交改动审查；或 `/code-review <pr>` 审查 GitHub PR（拉 diff、跑校验、发布 review）

**Agent（5 个）：**
- **`code-reviewer`** — 语言专家未命中时的通用兜底
- **`python-reviewer`** — PEP 8、Pythonic 惯用法、类型注解、安全（bandit）、Django/FastAPI/Flask 模式
- **`typescript-reviewer`** — 类型安全、async 正确性、React/Next.js 模式、Node 安全
- **`swift-reviewer`** — Swift 6 并发、值类型、actor 模式、SwiftUI、Keychain/ATS 安全
- **`security-reviewer`** — OWASP Top 10、密钥检测、注入、不安全加密。`/code-review` **每次都会自动跑**，不论语言。

---

## research

研究和 LLM 工程：

- **`search-routing`** — 按查询特征在 exa / firecrawl / linkup 里选一个搜索 MCP；自动挑最便宜够用的，deep 模式需确认
- **`research`** — 多源研究（firecrawl + exa MCPs）+ 引用；按场景的采集清单：投资人尽调 / 竞品 / 市场规模 / 供应商
- **`cost-aware-llm-pipeline`** — 按复杂度路由模型、预算追踪、prompt cache
- **`regex-vs-llm-structured-text`** — 解析决策框架：先正则，低置信度才上 LLM

---

## skills

Skill 管理：

- **`skill-stocktake`** — 审计 Claude skill / 命令质量（Quick Scan + Full）
- **`skill-comply`** — 可视化 skill / rules / agent 是否真被遵守
- **`rules-distill`** — 从 skill 抽跨切原则成 rules

---

## business

融资：

- **`investor-materials`** — Pitch deck、一页纸、备忘录、加速器申请、财务模型；附 Outreach 小节：day 0 → day 4–5 → day 10–12 的跟进节奏

---

## codex

通过 Codex MCP 拿第二意见 — 只读，不改代码：

- **`codex-review`** — 默认代码审查入口。Codex 按多语言审查方法论跑（严重度矩阵、`file:line`、强制安全检查）。只有明确要 Claude subagent 或要自动改 in-scope 问题时才退回 `code-review`。
- **`design-challenge`** — 质疑方案本身而非代码。返回假设 / 失败模式 / 备选方案，不是 bug 列表。

---

## session-summary

只有 hooks 和脚本，没有 skill。会话结束时打印会话分析面板（15 个可配置区块）。Vendored 自 [FlorianBruniaux/claude-code-plugins](https://github.com/FlorianBruniaux/claude-code-plugins)，MIT 协议。

---

## 安装

把这个 marketplace 加进 Claude Code：

```bash
claude plugin marketplace add Davie521/claude-skills
```

然后单独安装 plugin：

```bash
claude plugin install dev-workflow@yifan-personal
claude plugin install design@yifan-personal
claude plugin install swift@yifan-personal
# ... 等等
```

或一次装 15 个：

```bash
for p in dev-workflow document work-tools writing design swift web data quality code-review research skills business codex session-summary; do
  claude plugin install "$p@yifan-personal"
done
```

## 使用

```
> /cpr                            # 完整 PR 流水线，CI 全绿自动合并（说 'cl' 也能触发）
> 帮我写一篇关于...的文章         # 触发 vibe-writing
> 做一张...的速查表               # 触发 cheatsheet
> 深度研究 X                      # 触发 research
> 帮我审查这段代码安全性          # 触发 security-review
```

大部分 skill 通过自然语言匹配自动触发。

## 依赖

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- GitHub CLI (`gh`) — cpr 工作流需要
- 飞书 MCP server — `feishu` skill 需要
- 各类 API key 按 skill 不同（Exa / firecrawl / Context7 等）

## 许可证

MIT
