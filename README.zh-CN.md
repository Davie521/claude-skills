# Claude Skills

[English](README.md) | **中文**

Yifan 个人 Claude Code 插件市场 — **13 个 plugin / 116 个 skill**，覆盖开发工作流、设计、语言模式、测试、研究等。

## Plugin 总览

| Plugin | Skill 数 | 用途 |
|--------|---------|------|
| [`dev-workflow`](#dev-workflow) | 15 | Git PR 自动化、多 Agent 实现、蓝图、浏览器路由、**拷问、调试纪律、架构深化、issue triage** |
| [`document`](#document) | 7 | A4 速查表、文档协作、PDF、文档查询、代码库 onboarding |
| [`work-tools`](#work-tools) | 1 | 飞书集成 |
| [`writing`](#writing) | 5 | Vibe 写作、文章、内容引擎、跨平台发布、视频编辑 |
| [`design`](#design) | 23 | UI/UX Pro Max 设计家族 — 设计系统、样式、动效、审计 |
| [`python`](#python) | 7 | Python + Django：模式、测试、安全、验证 |
| [`swift`](#swift) | 6 | Swift/iOS：SwiftUI、并发、持久化、端上 LLM |
| [`web`](#web) | 9 | TS 前端、Node 后端、MCP server、Docker、部署 |
| [`data`](#data) | 5 | PostgreSQL、ClickHouse、迁移、PyTorch、自动爬虫 |
| [`quality`](#quality) | 14 | 测试、E2E、性能基准、安全审查、编码规范 |
| [`research`](#research) | 8 | 深度研究、Prompt 优化、成本感知 LLM 管道 |
| [`skills`](#skills) | 13 | Skill 管理 — 创建、审计、演进、升级 |
| [`business`](#business) | 3 | 投资人沟通、Pitch 材料、产品评估 |

---

## dev-workflow

自动化开发工作流。

#### `/cpr` — Git PR 流水线

一条命令从本地改动到 PR 就绪。Claude 自动完成：

1. 检测当前 git 状态（未提交更改、已有 PR、CI 状态）
2. 提交并推送代码，通过 `gh` 创建 PR
3. 用 `gh pr checks --watch` 监听 CI
4. CI 失败：读取错误日志 → 修复代码 → 重新推送
5. CI 通过：审查 Copilot 评论，修复真正问题（忽略误报）
6. 循环步骤 3–5 直到全部通过

#### `/cl` — Copilot Lint 审查

审查已有 PR（不创建新 PR）：

- 检查 CI 状态，本地修复 build/lint 错误
- 拉取 PR 上的 Copilot 审查评论
- **批判性评估每条建议** — 只修真正的 bug、安全问题、有实际收益的改进
- 忽略过度防御、误报、纯风格偏好
- 循环直到 CI 通过且所有有效评论处理完

#### `/impl` — 多 Agent 协作实现

为大型功能编排一支专业 Agent 团队：

| 阶段 | Agent | 做什么 |
|------|-------|--------|
| 0 | **Planner** | plan mode 中 2–3 轮计划迭代 |
| 1 | **Implementer** | 在隔离的 git worktree 中按计划写代码 |
| 2 | **Reviewer** | 代码审查（计划、规范、安全、无障碍） |
| 3 | **Tester** | 运行测试、Playwright 截图、当场修 bug |
| 4 | **Reviewer** | 最终审查测试修复 |
| 5 | **收尾** | 整理 commit 历史、建分支、建 PR |

#### `browser` — 浏览器 MCP 路由

根据意图自动选浏览器工具：

| 意图 | MCP |
|------|-----|
| 浏览、填表、打开页面 | **browser-use** |
| 性能、调试、网络、console | **Chrome DevTools** |
| E2E 测试 | **Playwright** |

#### 其他 dev-workflow skills

- **`blueprint`** — 把一句话目标变成多 session 多 agent 施工蓝图，自带依赖图、并行检测、对抗式 review gate
- **`git-workflow`** — 分支策略、commit 规范、merge vs rebase、冲突解决
- **`repo-scan`** — 跨语言代码资产审计，分类每个文件，找第三方库 / 死代码
- **`grill-me`** — 让 Claude **反过来无情拷问你**的 plan，一次一个问题，每问给推荐答案，直到决策树每条分支都 resolve（轻量版，不写文档）
- **`grill-with-docs`** — 同样的拷问，但**实时更新** `CONTEXT.md`（领域术语表）和 `docs/adr/`（架构决策），是 CONTEXT.md 文化的生产者
- **`diagnose`** — 6 阶段调试纪律（构造反馈回路 → 复现 → 列 3-5 个排序假设 → 用 `[DEBUG-xxxx]` 唯一前缀打探针 → 修复+回归测试 → 清理 grep）针对疑难 bug 和性能回归
- **`improve-codebase-architecture`** — 找架构深化机会（强制使用 Module / Interface / Depth / Seam 术语 + "deletion test" 启发式），列候选 → 用户挑一个 → drop into 拷问
- **`prototype`** — 抛弃式原型，强制二分支决策：逻辑/状态问题 → 终端交互 TUI；UI 问题 → 同路由多变体切换栏
- **`to-prd`** — 把当前会话直接合成成 PRD（**不再 interview**），发到 GitHub issue 或存到 `docs/prds/`
- **`triage`** — Issue 5 状态机（needs-triage / needs-info / ready-for-agent / ready-for-human / wontfix），自带 `.out-of-scope/` 拒绝知识库
- **`caveman`** — 持续压缩 ~75% token 的回复模式，删冠词/客套话但保留所有技术内容

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
- **`docs`** — 通过 Context7 查任意库 / 框架的最新文档
- **`codebase-onboarding`** — 给陌生代码库生成上手指南（架构图、入口、约定、起始 CLAUDE.md）
- **`architecture-decision-records`** — 把会话中的架构决策记录为结构化 ADR
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

#### 其他 writing skills

- **`article-writing`** — 长文写作，保持声音一致性
- **`content-engine`** — X / LinkedIn / TikTok / YouTube / newsletter 平台原生内容
- **`crosspost`** — 多平台分发，按平台适配（不复制粘贴）
- **`video-editing`** — AI 辅助视频剪辑（FFmpeg / Remotion / ElevenLabs / fal.ai）

---

## design

UI/UX Pro Max 设计家族 — 23 个 skill 覆盖完整设计生命周期：

**基础（5）：** `ui-ux-pro-max`（路由器，67 styles / 96 palettes / 13 stacks）, `ui-styling`（shadcn/ui + Tailwind）, `design-system`（token 架构）, `brand`, `teach-impeccable`

**增强（4）：** `delight`, `bolder`, `colorize`, `overdrive`

**克制（4）：** `quieter`, `distill`, `normalize`, `harden`

**专项（7）：** `optimize`, `adapt`, `arrange`, `typeset`, `clarify`, `onboard`, `extract`

**评估（3）：** `audit`, `critique`, `codebase-to-course`

---

## python

Python 和 Django 模式：

- **`python-patterns`** — Pythonic 惯用法、PEP 8、类型注解
- **`python-testing`** — pytest、TDD、fixture、mock、覆盖率
- **`python-review`** — 全面代码审查
- **`django-patterns`** — Django 架构、DRF、ORM、缓存
- **`django-security`** — 认证授权、CSRF、SQL 注入、XSS、安全部署
- **`django-tdd`** — pytest-django、factory_boy、DRF 测试
- **`django-verification`** — 迁移、lint、测试、安全扫描、部署就绪

---

## swift

Swift 和 iOS 开发：

- **`swiftui-patterns`** — SwiftUI 架构、`@Observable`、导航、性能
- **`swift-concurrency-6-2`** — Swift 6.2 Approachable Concurrency、`@concurrent`、isolated conformances
- **`swift-actor-persistence`** — 用 actor 实现线程安全持久化（内存缓存 + 文件存储）
- **`swift-protocol-di-testing`** — 基于协议的依赖注入，便于测试
- **`liquid-glass-design`** — iOS 26 Liquid Glass 材质（模糊、反射、形变）
- **`foundation-models-on-device`** — Apple FoundationModels 端上 LLM（`@Generable`、工具调用、流式）

---

## web

TypeScript / Node Web 全栈：

- **`frontend-patterns`** — React、Next.js、状态管理
- **`nextjs-turbopack`** — Next.js 16+ Turbopack
- **`bun-runtime`** — Bun 作为运行时 / 包管理 / 打包 / 测试
- **`backend-patterns`** — Node/Express/Next API 最佳实践
- **`api-design`** — REST API 模式（资源命名、状态码、分页、错误、版本）
- **`mcp-server-patterns`** — TS SDK 写 MCP server（tools、resources、Zod、stdio vs HTTP）
- **`docker-patterns`** — Docker + Compose 本地开发、安全、网络
- **`deployment-patterns`** — CI/CD、容器化、健康检查、回滚
- **`content-hash-cache-pattern`** — SHA-256 内容哈希缓存

---

## data

数据工程和 ML：

- **`postgres-patterns`** — 查询优化、schema 设计、索引、安全
- **`clickhouse-io`** — 分析数据库模式和查询优化
- **`database-migrations`** — 零停机 schema 变更（PostgreSQL / MySQL / Prisma / Drizzle / Django）
- **`pytorch-patterns`** — 训练管道、模型架构、数据加载
- **`data-scraper-agent`** — 100% 免费 GitHub Actions 数据采集 agent（Gemini Flash + Notion/Sheets/Supabase）

---

## quality

代码质量、测试、审查：

**测试（8）：**
- **`tdd-workflow`** — TDD 80%+ 覆盖率（单元 + 集成 + E2E）
- **`e2e`** — 生成并跑 Playwright E2E 测试 + 产物
- **`e2e-testing`** — Page Object Model、CI/CD 集成、flaky 测试策略
- **`benchmark`** — 性能基线、回归检测
- **`browser-qa`** — 部署后视觉测试和 UI 验证
- **`click-path-audit`** — 追踪每个按钮的状态变化（找 UI 不一致）
- **`canary-watch`** — 监控部署 URL 防回归
- **`ai-regression-testing`** — 抓 AI 自审盲点（同一模型既写又审）

**审查（6）：**
- **`security-review`** — 完整安全审查清单（认证 / 输入 / 密钥 / API）
- **`security-scan`** — 扫描 `.claude/` 配置漏洞（CLAUDE.md / settings / hooks / agents）
- **`coding-standards`** — TypeScript / JavaScript / React / Node 通用规范
- **`plankton-code-quality`** — 写时自动 format/lint/fix（每次编辑触发）
- **`safety-guard`** — 防止生产环境 / 自主 agent 的破坏性操作
- **`santa-method`** — 多 agent 对抗式验证（两个独立 reviewer 都通过才 ship）

---

## research

研究和 LLM 工程：

- **`deep-research`** — 多源研究（firecrawl + exa MCPs）+ 引用
- **`market-research`** — 竞品分析、投资人尽调
- **`search-first`** — 写代码前先搜现成方案
- **`exa-search`** — Exa MCP 神经搜索（Web、代码、公司）
- **`iterative-retrieval`** — 子 agent 上下文问题的渐进式检索
- **`prompt-optimize`** — 分析草稿 prompt 输出优化版（advisory，不执行）
- **`cost-aware-llm-pipeline`** — 按复杂度路由模型、预算追踪、prompt cache
- **`regex-vs-llm-structured-text`** — 解析决策框架：先正则，低置信度才上 LLM

---

## skills

Skill 和 instinct 管理系统：

- **`skill-create`** — 从 git 历史抽模式生成 SKILL.md
- **`skill-comply`** — 可视化 skill / rules / agent 是否真被遵守
- **`skill-stocktake`** — 审计 Claude skill / 命令质量（Quick Scan + Full）
- **`skill-health`** — Skill 组合健康仪表盘
- **`learn-eval`** — 从会话抽可复用模式 + 自评 + 决定保存范围
- **`promote`** — 把项目级 instinct 升级到全局
- **`prune`** — 删除 30 天未升级的 instinct
- **`evolve`** — 分析并演进 instinct 结构
- **`projects`** — 列项目 + instinct 统计
- **`rules-distill`** — 从 skill 抽跨切原则成 rules
- **`instinct-status`** — 显示已学 instinct（项目 + 全局）+ 置信度
- **`instinct-import`** / **`instinct-export`** — 跨机器同步 instinct

---

## business

融资和产品评估：

- **`investor-outreach`** — 投资人 cold email、warm intro、跟进、月度 update
- **`investor-materials`** — Pitch deck、一页纸、备忘录、加速器申请、财务模型
- **`product-lens`** — 建立"为什么"、产品诊断、模糊想法变规格

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
claude plugin install python@yifan-personal
# ... 等等
```

或一次装 13 个：

```bash
for p in dev-workflow document work-tools writing design python swift web data quality research skills business; do
  claude plugin install "$p@yifan-personal"
done
```

## 使用

```
> /cpr                            # 跑完整 PR 流水线
> /cl                             # 审查并修复 Copilot lint
> /impl                           # 多 Agent 协作实现
> /docs react server components   # 查 React 最新文档
> 帮我写一篇关于...的文章         # 触发 vibe-writing
> 做一张...的速查表               # 触发 cheatsheet
> 深度研究 X                      # 触发 deep-research
> 帮我审查这段代码安全性          # 触发 security-review
```

大部分 skill 通过自然语言匹配自动触发。

## 依赖

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- GitHub CLI (`gh`) — cpr/cl 工作流需要
- 浏览器 MCP server — `browser` skill 需要
- 飞书 MCP server — `feishu` skill 需要
- 各类 API key 按 skill 不同（Exa / firecrawl / Context7 等）

## 许可证

MIT
