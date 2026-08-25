# Claude Skills

[English](README.md) | **中文**

Yifan 个人 Claude Code 插件市场 — **15 个 plugin / 50 个 skill + 5 个 review agent + 1 个 review 命令**，覆盖开发工作流、设计、语言模式、测试、研究等。

每个 skill 的标题就点明它解决什么，下面写清**触发**（怎么让它上场）和**机制**（它内部实际怎么跑）；标题不够说明白的，另起一行 **定位** 补上。

## Plugin 总览

| Plugin | Skill 数 | 用途 |
|--------|---------|------|
| [`dev-workflow`](#dev-workflow) | 10 | Git PR 自动化（含自动合并）、深度规划、**拷问、调试纪律、架构深化、issue triage** |
| [`document`](#document) | 5 | A4 速查表、文档协作、PDF、签证文档翻译、codebase-to-course |
| [`work-tools`](#work-tools) | 1 | 飞书集成 |
| [`writing`](#writing) | 3 | Vibe 写作（含声音捕捉）、多平台分发、视频编辑 |
| [`design`](#design) | 2 | UI/UX Pro Max、UX critique |
| [`swift`](#swift) | 4 | Swift/iOS：SwiftUI + 架构模式、并发、Liquid Glass、端上 LLM |
| [`web`](#web) | 6 | REST API、MCP server、Docker、部署、Bun、内容哈希缓存 |
| [`data`](#data) | 2 | 迁移 + PostgreSQL 速查、自动爬虫 |
| [`quality`](#quality) | 8 | TDD、E2E、安全审查/扫描、对抗式验证 |
| [`code-review`](#code-review) | 5 agent + 1 命令 | `/code-review` 自动按语言分发到 Python/TypeScript/Swift 专家 + 强制 security 审查 |
| [`research`](#research) | 3 | 深度研究（含市场调研）、搜索路由、LLM 成本纪律 |
| [`skills`](#skills) | 3 | Skill 管理 — 盘点、合规审计、规则蒸馏 |
| [`business`](#business) | 1 | 投资人材料 + outreach 跟进节奏 |
| [`codex`](#codex) | 2 | Codex MCP 第二意见 — 代码审查、方案质疑 |
| [`session-summary`](#session-summary) | 仅 hooks | 会话总结 hooks 和脚本（无 skill） |

**实际使用量排序**（按 skill 注入次数统计，不是工具调用数）：`deep-plan` › `/cpr` › `santa-method` › `research` › `ui-ux-pro-max`。这五个是日常主力，其余是「话题一来就上场」的参考资料 —— 零调用不等于没价值，很多 skill 就是等着某个特定场景出现的。

---

## dev-workflow

自动化开发工作流。整个仓库的主力组 —— `deep-plan` 和 `/cpr` 是使用量前二。

### `/cpr` — Git PR 流水线

**定位**：一条命令从本地改动走到 PR 合并完成，中途不停下来问，每步做完直接继续下一步。
**触发**：说 `cpr` 或 `cl`（原 Copilot Lint 审查工作流已并入，`cl` 仍能触发）

先检测状态再决定从哪接续 —— `gh pr view --json number,state`、`gh pr checks`、`git status` 三条命令定位入口（无 PR → 从建 PR 开始；CI 运行中 → 等；CI 失败 → 查错修复；CI 通过 → 检查 Copilot 评论；全绿且评论已处理 → 合并）。

1. **检查分支** —— 在 `main` 上则先切一个新分支
2. **提交更改** —— `git add` + `git commit`
3. **推送 + 建 PR** —— `git push -u` + `gh pr create`
4. **等待 CI** —— `gh pr checks --watch`；出现 `no checks reported` 时用 `[ -d .github/workflows ]` 落实一下是不是真没 CI，是就跳到第 6 步
5. **CI 失败时** —— `gh run view <id> --log-failed` 读日志 → 修复 → 推送
6. **Copilot 评论** —— 审查没自动触发就先手动请求，再拉 `gh pr view --comments` **加上** `gh api repos/{owner}/{repo}/pulls/$PR_NUMBER/comments` → 逐条评估 → 只修必要的 → 推送
7. **循环 4–6** 直到全部通过
8. **自动合并** —— 全部检查通过且无未处理 review → `gh pr merge --merge --delete-branch`；若有 review 请求变更或未通过，暂停合并并通知你

第 6 步是这个 skill 真正有主见的地方 —— **不要盲目修改所有 Copilot 建议**：

| 必须修改 | 可以忽略 |
|----------|----------|
| SQL 注入、XSS、敏感信息泄露 | 过度防御的建议 |
| 实际会导致问题的 Bug | 假阳性、误报 |
| 严重影响可读性的风格问题 | 纯粹的风格偏好 |
| 明显的性能问题 | 微优化、过早优化 |
| 有实际收益的改进 | 教条式建议 |

判断标准：当前上下文是否真有问题？修改有实际收益？符合项目需求？每条评论输出显式决策 —— `需要修改: [原因]` / `忽略: [原因]`。

> **它固化了三个坑**。*评论分两处*：Copilot 的行内 review 评论只存在于 REST 的 `repos/{owner}/{repo}/pulls/<n>/comments` 响应里，`gh pr view --comments` 只返回会话级评论 —— 只查后者会漏掉**全部**代码评论。*退出码 1 有歧义*：`gh pr checks` 在「检查失败」和「这个 commit 没有任何 check」（`no checks reported`）两种情况下都非零，后者不是失败、不能拿它阻塞合并；但它只证明「没跑过检查」，要断定仓库没有 CI 还得对着 `.github/workflows` 落实一次。*审查常要主动请求*：Copilot 不一定自动触发，而且只有 `copilot-pull-request-reviewer[bot]` 这个带后缀的 slug 请求得动（写 `Copilot` 报 not found，裸 slug 报 422）；请求后评论要 2–3 分钟才出，得轮询而不是查一次就下结论。

### `deep-plan` — 写码前的强制规划闸门

**定位**：复述、评风险、分阶段，等你点头才动手。使用量全库第一。
**触发**：开新功能、架构改动、复杂重构、多文件改动或需求不清时自动；也可直接说 deep-plan

- **Phase A（只读）**：复述需求和依赖 → 评估风险与复杂度 → 给分阶段计划 → **硬性等待**明确批准（yes / proceed / 确认）。支持 `modify:`、`different approach:`、`skip phase 2` 这类指令改计划，而不是推倒重来。
- **Phase B（批准后第一动作）**：建隔离 worktree，默认 `git worktree add ../<repo>_<slug>` 兄弟目录、分支 `plan-<slug>`（目录与分支绑定，不各起各的）—— 嵌套树跑不了 docker bind-mount，只在无 docker 的简单仓库里才作为备选。
  - 三个「看着对其实不对」的检查：`git rev-parse --show-toplevel` 分不出主树和链接树（两种都只返回一个路径）；改比 `--git-dir` 和 `--git-common-dir` **也得加 `--path-format=absolute`**，否则在子目录里一个绝对一个相对，主树会被误判成链接树；`git symbolic-ref refs/remotes/origin/HEAD` 在 origin/HEAD 未设时是 **fatal 不是空输出**，要先 `git remote set-head origin -a`。
- **Phase C**：树内实现，完成后交接 `/cpr` 或 code review。

> **注**：绝不在主 worktree 上直接改 —— 这是这个 skill 的硬性前提，不是建议。

### `cleanup` — 会话收尾的四阶段

**定位**：把「现场」真正打扫干净，每个阶段必须给出带证据的结论。
**触发**：说 cleanup / 收尾 / 清理现场 / 打扫，或长任务交接前

1. **关进程**：kill 前用 `ps -o pid,ppid,lstart` 和 `lsof` 核血统 —— 孤儿进程会 reparent 给 launchd，靠 PPID 认亲会杀错人；带 `restart: unless-stopped` 的 docker stack 必须拆栈，只杀容器会被自动拉起来。
2. **文档同步**：以代码为准改文档，**绝不反向**改代码去迁就文档；同时回扫对话里「把 README 更新一下」这类说过但没执行的遗言。
3. **任务清零**：TaskList 逐项过、本次新引入的 TODO、临时文件用 `trash` 清（可恢复，不用 `rm -rf`）。
4. **记忆沉淀**：只存跨会话仍成立的知识；Global vs Project 有判断规则（拿不准选 Global）；优先并入已有记忆文件而不是新建。

最后输出四行证据表。**瞒报才算失败** —— 「本阶段无需处理」是完全合法的结论，静默跳过不是。

### `diagnose` — 疑难 bug 的六阶段调试纪律

**定位**：防止乱枪打鸟，每一步都产出可证伪的证据。
**触发**：说 diagnose / debug this，或描述某个东西坏了、报错了、变慢了

构造反馈回路（先有能快速验证的手段，否则后面全是猜）→ 复现 → 列 3-5 个按可能性排序的假设 → 用 `[DEBUG-xxxx]` 唯一前缀打探针（事后一次 grep 清干净）→ 修复 + 补回归测试 → 清理全部探针。核心是不允许「我觉得是这里」就直接改。

### `grill-with-docs` — 反过来拷问你，同时把结论写进文档

**定位**：一次一题地攻击你的 plan，把结晶出来的术语和决策实时写进项目文档 —— `CONTEXT.md` 文化的生产者。
**触发**：说 grill me，或要求 stress-test / 挑战一个方案

一次只问一个问题，每问带推荐答案，对照项目领域模型（`CONTEXT.md` 术语表）逼问，直到决策树每条分支都 resolve。过程中实时更新 `CONTEXT.md` 和 `docs/adr/`。ADR 按内置 `ADR-FORMAT.md` 走三条准入门槛 —— **难以回头 / 缺上下文会惊讶 / 真实取舍的结果** —— 缺一即跳过，再加一道 consent gate 才落盘，这是防 ADR 泛滥的关键；`docs/adr/README.md` 维护索引表供回读。

> **注**：项目里没有 `CONTEXT.md` 时降级为轻量模式：只拷问，不写文档。

### `improve-codebase-architecture` — 系统性找架构深化机会

**定位**：不是凭感觉重构，而是用固定词汇把「哪里该深化」找出来。
**触发**：想改善架构、找重构机会、让模块更可测/更好被 AI 导航时

强制使用 Module / Interface / Depth / Seam 这套术语分析代码库，配合 deletion test 启发式（「删掉这个抽象会怎样」）找出候选深化点，列给你挑；选定后 drop into 拷问流程验证，最后交 `deep-plan` 落地。

### `prototype` — 抛弃式原型

**定位**：在动真格之前把设计问题冲出来，只限两种场景。
**触发**：需要并排比较多个结构性不同的 UI 方案，或需要手动推一遍状态机 / 数据模型

强制二分支：逻辑 / 状态 / 数据模型问题 → 做一个可跑的终端 TUI，让你亲手把状态机推一遍；UI 问题 → 在同一个路由上做几个**结构性不同**的变体，加切换栏并排比。产出明确是丢弃品，不追求代码质量。

> **注**：触发面是刻意收窄的（"mock up a UI" 这类泛化触发词已删），防止普通 UI 需求误入。要做真页面用 `ui-ux-pro-max` / Hallmark。

### `to-prd` — 把当前会话直接合成 PRD

**定位**：不再重新访谈，直接把已有对话变成文档。
**触发**：讨论完需求后说 to-prd

从对话上下文提取目标、范围、决策和约束，直接产出 PRD，发到 GitHub issue 或存 `docs/prds/`。关键行为约束是**不再 interview** —— 它假设该问的在对话里已经问过了。

### `triage` — Issue 分诊状态机

**定位**：把进来的 bug / 需求分拣到该去的地方，并且记住拒绝过什么。
**触发**：建 issue、分诊、给 AFK agent 备料时

五状态：needs-triage / needs-info / ready-for-agent / ready-for-human / wontfix，每个状态有明确准入条件和下一步动作。自带 `.out-of-scope/` 拒绝知识库 —— 被 wontfix 的东西记一次原因，同类请求再来时直接引用并链接过去，不用重新辩论一遍。

### `caveman` — 持续压缩回复模式

**定位**：砍冠词、填充词、客套话，保留全部技术内容。
**触发**：**仅显式调用** —— `/caveman` 或说 caveman mode

进入后持续生效，直到显式退出（stop caveman / normal mode / exit caveman）。压缩手段主要针对英文输出（删 a/an/the、just/really，缩写 DB/auth/config），中文交互收益有限 —— 中文本来就没有冠词。

> **注**：「说简短点」不会触发它 —— 那是一次性风格要求，不该掉进一个持久模式。

---

## document

### `cheatsheet` — A4 速查表生成器

**定位**：从 Markdown 生成考试级密度的可打印速查表。
**触发**：要做速查表 / cheatsheet / 考前小抄 / 浓缩参考卡时

A4 横版、5 栏布局、6pt 字体的极限密度排版，支持 LaTeX 数学公式、表格、高亮块、注释、多页输出。流程：按自定义语法写 `.md` → `python3 "${CLAUDE_PLUGIN_ROOT}/skills/cheatsheet/scripts/md2html.py" input.md -o output.html` → 浏览器打印成 PDF。转换脚本零依赖（纯 Python 标准库），语法规范见 `references/cheatsheet_spec.md`。

### `pdf` — PDF 全套处理

**定位**：提取、生成、表单填写、OCR 的 9 个可跑脚本。
**触发**：处理 PDF —— 抽文本表格、填表单、拆合页面、转图片

表单流程是最完整的一条链：`check_fillable_fields.py` 判断这份 PDF 到底能不能填 → `extract_form_field_info.py` 提字段信息 → `fill_fillable_fields.py` 填写。不可填的走标注路线，优先用精确坐标而不是靠肉眼估：`extract_form_structure.py`（pdfplumber）直接从 PDF 里读出文字标签、横线和复选框方块，只有扫描件才退回到裁剪放大的视觉估算 → `check_bounding_boxes.py` 查重叠和框太小 → `fill_pdf_form_with_annotations.py` 自动识别 `fields.json` 用的是 PDF 点还是图片像素坐标并相应填写 → `create_validation_image.py` 生成验证图（图片坐标流程），肉眼确认位置对不对。

> **前置**：先 `python3 -m venv` 建虚拟环境（明确禁止 `--break-system-packages`）；`pdf2image` 另需系统装 poppler。

### `doc-coauthoring` — 结构化协作写文档

**定位**：合写提案 / 技术规格 / 决策文档，三阶段推进，绝不整文重写。
**触发**：要合写一份正经文档时

① 收集上下文：澄清式提问 → 头脑风暴 → 素材筛选循环；② 用 Write 建骨架，章节先占位；③ 用 Edit 逐节起草和外科手术式修订，每次改动后确认。还能派子 agent 做 **Reader Testing** —— 模拟目标读者从头读一遍，报告哪里读不通、哪里缺前提。

### `visa-doc-translate` — 签证材料翻译

**定位**：把签证申请材料（图片）翻成英文，出中英双语 PDF。
**触发**：处理签证申请材料翻译时

HEIC→PNG（`sips`）→ EXIF 旋转矫正 → 模型直接读图并翻译 → PIL + reportlab 排双语 PDF 输出。

> **注**：不用 OCR 库 —— 实测 Claude 直接读图比挂三个可能根本没装上的 OCR 后端可靠；认不清的一律标 `[illegible]`，绝不猜。签证材料猜错一个字就是麻烦。

### `codebase-to-course` — 代码库变交互式课程

**定位**：把任意代码库变成给零基础读者的单文件 HTML 课程。
**触发**：说 turn this into a course / 讲讲这个代码库怎么工作 / 做个交互式教程

目标读者是 **vibe coder** —— 会指挥 AI 写码但没受过 CS 训练的人。四阶段：深读代码库（追数据流、找出「角色」）→ 设计 5-8 个模块的课纲（从用户已知的行为层层下钻）→ 生成单文件 HTML → 浏览器打开走查。五种交互元素强制齐全：组件群聊动画、数据流动画、代码 ↔ 白话对照、场景式测验、术语 tooltip。内容纪律：代码原样不许精简、隐喻不许复用（禁餐厅梗）、每屏至少一半是视觉元素。

---

## work-tools

### `feishu` — 飞书 / Lark 集成

**定位**：通过 MCP 操作飞书 —— 发消息、建群、建文档、传文件、查人。
**触发**：提到飞书 / Lark，或要发消息到飞书群 / 建飞书文档 / 查联系人时

走官方 lark-mcp CLI 的 MCP server（工具形如 `mcp__feishu__im_v1_message_create`），覆盖 IM、docx、drive、wiki 四类 API。

> **前置**：feishu MCP server 需已配置。工具不在时，skill 会明确提示你去配置，而不是瞎猜 API 形状。

---

## writing

### `vibe-writing` — 四阶段协作写作

**定位**：你主导、AI 辅助，**保留你的原话**而不是替你重写。
**触发**：说 写作 / 写文章 / 帮我写 / vibe

| 阶段 | 触发词 | 做什么 |
|------|--------|--------|
| **学习** | 默认 | 苏格拉底式对话，每 4 轮固化一张知识卡片 |
| **结构** | "结构" | 给 2–3 种文章骨架（问题-方案 / 对比 / 递进 / 故事 / 清单 / SCQA） |
| **写作** | "写作" / "迭代" | "整理"做整合，"润色"做事实核查 + 语言优化 |
| **成稿** | "成稿" | 串联输出卡片 + 过渡段落 + 开头结尾 |

声音一致性有两个硬工具：**五维声音捕捉清单**（句长节奏 / 语气 / 惯用修辞 / 幽默接受度 / 排版习惯）和 **AI 腔禁用词表**（套话开头、Moreover/Furthermore、game-changer / 赋能 —— 出现即删改）。

### `crosspost` — 一份素材写成七个平台的原生版本

**定位**：多平台分发，每个平台单独原生化；**只起草，不发布**。
**触发**：要把一份内容分发 / 复用到多个平台时

覆盖 X / LinkedIn / Threads / Bluesky / TikTok / YouTube / newsletter 七个目标，各带字数上限、链接处理方式、话题标签惯例和原生化要点（TikTok 前 3 秒抢注意力；YouTube 结果前置、按章节组织；newsletter 单一视角、可扫读）。repurposing cascade：锚定资产 → 提取 3-7 个原子观点 → 逐平台原生改写 → 去重 → CTA 对齐各平台意图。

> **注**：绝不同文跨发。发布动作由你执行，skill 附错峰排期建议。

### `video-editing` — 真实素材的 AI 辅助剪辑管线

**定位**：从原始拍摄到成片的五层流水线。
**触发**：剪视频、做 vlog、把散素材结构化时

素材摄取（VideoDB Python SDK，桌面录制带实时上下文）→ FFmpeg 粗剪 → Remotion 程序化合成 → ElevenLabs 配音 → fal.ai 生成补充素材 → Descript / CapCut 精修。每层给的是可直接跑的命令和代码，不是概念图。

---

## design

两个 skill。反 AI 味的纪律交给 [Hallmark](https://github.com/Nutlope/hallmark)，
可测量的无障碍 / 性能审计交给 `chrome-devtools` MCP 的 `lighthouse_audit`。
这个插件只覆盖那两者都不做的部分。

### `ui-ux-pro-max` — 设计知识库 + 项目设计系统生成器

**定位**：可搜索的设计选型库，外加把选定结果固化成项目设计系统。使用量全库第五。
**触发**：建站、做 landing page、UI 风格 / 配色 / 字体 / 图表选型时

67 风格 / 96 配色 / 57 字体搭配 / 25 图表 / 13 技术栈的 CSV 库，`scripts/search.py` 做 BM25 检索。`--design-system --persist` 生成 `design-system/<project-slug>/MASTER.md` 和 pages/ 页面级覆盖，同时在项目根放一个 `design.md` 指针 —— 让 Hallmark 把这个项目识别为「系统托管」，而不是误报 variety drift。官方设计系统路由表见 `reference/design-system-map.md`，覆盖 Fluent / Material 3 / Carbon / Polaris / Atlaskit / Primer / govuk-frontend / USWDS 八家。

### `critique` — UX 体验评估

**定位**：回答「这个体验成不成立」，而不是「看起来像不像 AI 做的」。
**触发**：说 review / critique / 评审这个设计

10 个维度打分（视觉层级、信息架构、认知负荷、情绪旅程含峰终定律、可发现性等），从 5 个用户原型里自动挑 2-3 个最相关的 persona 做代入测试，输出红旗清单和可执行反馈。发现语气不匹配（比如严肃产品用了俏皮文案）时会先问你是不是有意的。

> **分工**：只诊断，不动手；产出或修改设计归 `ui-ux-pro-max`。

那 20 个单动词 skill（`bolder` / `quieter` / `distill` / `audit` …）已于
2026-08-08 移除：零调用，且它们的调度入口依赖一个被禁用的 `frontend-design`。

---

## swift

保留下来的都是**训练截止之后的版本特定知识** —— 也就是模型靠记忆不可靠的那部分。

### `swiftui-patterns` — SwiftUI 架构与状态管理

**触发**：SwiftUI 架构、状态管理、导航、性能问题时

`@Observable` 时代的状态管理（`@State` + `@Observable` 视图模型、`@Environment` 注入）、导航模式、性能优化。Architecture Patterns 区收了两个成型模式：

- `LocalRepository<T>` actor —— 内存字典缓存 + 原子 JSON 落盘，**自带适用边界**：每次写都重写整个数据集，高频写或大数据集请换 GRDB / SwiftData
- 每边界一协议的依赖注入 —— `FileAccessor` 协议 + Mock + Swift Testing 双测试，代码自洽可编译

### `swift-concurrency-6-2` — Approachable Concurrency 迁移

**触发**：迁移 Swift 6.2 并发、要用 `@concurrent`、编译器报 data race 时

6.2 的核心变化：默认单线程（MainActor 默认推断），需要后台才显式 `@concurrent` 下放；isolated conformances 让 main actor 类型安全地遵守协议。针对「sending X risks causing data races」这类编译错误给具体解法。

### `liquid-glass-design` — iOS 26 Liquid Glass

**触发**：给原生 Apple 应用做 iOS 26 玻璃设计语言时

动态玻璃材质的模糊、反射、交互形变，覆盖 SwiftUI `glassEffect` / UIKit `UIGlassEffect` / WidgetKit 三处用法。

> **不是它**：网页毛玻璃（CSS `backdrop-filter` glassmorphism）不归它管，去 `ui-ux-pro-max`。description 里的消歧前缀就是为了防这个误路由。

### `foundation-models-on-device` — Apple 端上 LLM

**触发**：iOS 26+ 要用设备端模型做生成、引导式输出、工具调用时

会话与 `respond` 基本用法、`@Generable`/`@Guide` 引导式生成（直接产出类型化结构）、`Tool` 协议（`Arguments` / `Output` 两个关联类型，`call(arguments:)` 直接返回 `Output`，任何 `PromptRepresentable` 都行）、`ResponseStream` 的 snapshot 流式（迭代到的元素是 snapshot，取 `.content`）。

> **注**：顶层 `ToolOutput` 类型只存在于早期 iOS 26 seed，正式 SDK 里并不存在（`Transcript.ToolOutput` 是另一个无关的结构）。文档里 8 个代码块全部对照本机 Xcode 26.6 SDK 跑过 `swiftc -typecheck`，零错误零警告。

---

## web

TypeScript / Node Web 全栈。职责已切干净：Docker 细节归 `docker-patterns`，部署策略归 `deployment-patterns`。

### `api-design` — REST API 设计决策

**触发**：设计或评审 REST 端点，纠结状态码 / 分页 / 版本方案时

资源命名规范、状态码选择（**422 带字段级错误详情**、**201 带 `Location` 头**）、offset vs cursor 分页取舍、过滤参数设计、版本化策略、限流模式。附一份 TypeScript / Next.js 参考实现（schema 校验 → 422 → 201 的完整链），同样的形状适用于任何栈。

### `docker-patterns` — Docker 与 Compose

**触发**：写 Dockerfile / compose、加固镜像、排查容器网络或卷问题时

开发 vs 生产 Dockerfile 分治、镜像加固、Compose 网络与卷策略、多服务编排。两个独有干货：

- `depends_on: condition: service_healthy` 用 healthcheck 门控启动顺序 —— 裸 `depends_on` 只等容器**起来**，不等服务**就绪**
- 匿名卷 `/app/node_modules` 防止宿主机 bind-mount 覆盖掉容器内装好的依赖

### `deployment-patterns` — 镜像之外的一切

**触发**：规划发布、搭 CI/CD、准备回滚预案时

rolling / blue-green / canary 三种 rollout 的取舍、CI/CD 流水线模式、健康检查端点 + k8s liveness / readiness / startup 三探针的分工、Zod 做环境变量 fail-fast 校验、跨平台回滚命令速查、上线前 checklist。Dockerfile 相关一律指向 `docker-patterns`。

### `mcp-server-patterns` — 写 MCP server

**触发**：要写、扩展或调试 MCP server 时

tools / resources / prompts 三种暴露方式、Zod 参数校验、stdio vs Streamable HTTP 传输选型、注册与调试的常见问题。最新 API 细节让你查 Context7 或官方文档，不在文里硬编码版本知识。

### `bun-runtime` — 什么时候该用 Bun

**触发**：技术选型或从 Node 迁移到 Bun 时

Bun 作为运行时 / 包管理器 / 打包器 / 测试运行器四个角色分别的成熟度和适用场景、从 Node 迁移的注意点、Vercel 支持现状。

### `content-hash-cache-pattern` — 内容哈希缓存

**触发**：缓存昂贵的文件处理结果（PDF 解析、OCR、文本抽取、图像分析）时

以文件内容的 SHA-256 而不是路径做缓存键：文件移动改名后缓存仍命中，内容一变自动失效；配合 service layer 分离，让缓存对业务代码完全透明。适合跨运行反复出现的重处理任务。

---

## data

### `database-migrations` — 零停机 schema 变更 + PG 速查

**触发**：写 SQL / 迁移、设计 schema 或索引、查慢查询、做 RLS 时

expand-contract 零停机模式、`CREATE INDEX CONCURRENTLY`、forward-only 纪律，覆盖 PostgreSQL 原生 / Prisma / Drizzle / Kysely / Alembic。

**Alembic 段基本都是坑**：autogenerate 把重命名当 drop+add（会丢数据，必须手写 `op.rename_table`）、检测不到 ENUM 加值和视图 / 触发器、`CONCURRENTLY` 要包 `autocommit_block`、heads 必须保持唯一。

**PostgreSQL 速查附录**：索引选型表（B-tree / GIN / BRIN 按查询模式选）、UPSERT、游标分页、`FOR UPDATE SKIP LOCKED` 做队列、RLS 里把 `auth.uid()` 包进 SELECT 的优化、慢查询和表膨胀诊断 SQL。

> **注**：Django 和 golang-migrate 两段按实际用不到的栈砍掉了。

### `data-scraper-agent` — 零成本定时采集 agent

**触发**：要搭一条免费的自动数据采集管道时（招聘、价格、新闻、GitHub、比分…）

GitHub Actions cron 驱动，Gemini 免费层做抽取，落地到 Notion / Sheets / Supabase，并能从用户反馈里学习。764 行的完整实施手册，不是示意图。模型 fallback 链是四个验证存在的 ID：`gemini-2.5-flash-lite` → `gemini-3.5-flash-lite` → `gemini-2.5-flash` → `flash-latest` 别名兜底。

> **注**：gemini-2.0 全家已被官方标注 Shut down；免费层限额官方已不发布固定数字，一律以 AI Studio dashboard 为准，文档里不写死。

---

## quality

代码质量、测试、审查。`santa-method` 是使用量全库第三。

### `santa-method` — 多 agent 对抗式验证

**定位**：两个互不知情的 reviewer 都通过，产出才允许 ship。
**触发**：要高置信度交付、要求「验证过再给我」时

同一轮里并行派两个独立 review agent，各自拿同样的评审 prompt，**互相不知道对方存在**；两个都通过才算过，任一不过就修复后进入下一轮 —— 且下一轮必须换全新 agent，消除「上次它说行」的锚定偏差。

> **分工**：确定性检查（build / lint / test）先跑，归 `tdd-workflow`；santa 只管语义层 —— 准确性、幻觉、遗漏。

### `tdd-workflow` — 测试驱动开发纪律

**触发**：写新功能、修 bug、重构时

核心是 **RED gate 反作弊**：红灯期间绝不重构、绝不「顺手改一下实现让测试过」—— 先让测试因**正确的原因**失败，再写最小实现。推纵向切片（一条完整用户路径的薄片）而非横向分层。80%+ 覆盖率是新代码的起点参考，不是拿来凑的教条；事后回归补测归 `ai-regression-testing`。

> **注**：Jest 的配置键是 `coverageThreshold`（单数），写成复数会让覆盖率闸门静默失效 —— 这个坑修过。示例里的领域对象来自上游项目，用的时候换成你自己的。

### `e2e-testing` — Playwright 端到端

**触发**：写 / 维护 E2E 测试，测试忽红忽绿时

Page Object Model 组织测试；trace 用配置项 `use: { trace: 'on-first-retry' }`（优先于手工 `context.tracing` 调用）；录像用 `use: { video: 'retain-on-failure' }`；CI 产物管理。

**抗 flaky 的关键认知**：竞态几乎不在 click（两种 click API 都会 auto-wait），而在断言侧做了一次性快照 —— 用会自动重试的 web-first 断言 `expect(locator).toHaveText()`，别先 `textContent()` 取值再断言。

### `ai-regression-testing` — 针对 AI 自审盲点的回归策略

**触发**：AI 辅助开发后要补回归、担心「同一个模型既写又审」失明时

沙箱模式 API 测试，不依赖数据库；用可复用的 `createTestRequest` harness 跑自动化 bug-check。立场鲜明：不追覆盖率百分比，按真实 bug 驱动补测。附一个 notification_settings 连续四轮回归的完整真实案例。

### `click-path-audit` — 逐个按钮追状态链

**触发**：系统性调试没找到 bug 但用户仍报按钮坏了；大重构动过共享状态之后

把每个用户可触达的按钮 / 触点，从点击到最终状态的完整序列画出来，找互相抵消的状态更新、错误的最终态、不一致的 UI 残留 —— 抓的是「每个函数单独都对、合起来错」这类 bug。是常规调试（`diagnose`）之后的补充手段，不是替代。

### `security-checklist` — 安全审查清单

**触发**：加 auth、处理用户输入、碰密钥、开 API、做支付等敏感功能时

覆盖认证、输入校验、密钥管理、API 安全、OWASP 常见项的检查清单和正反例代码。比如 Solana 签名验证给的是 tweetnacl 的 `nacl.sign.detached.verify` + `bs58.decode(publicKey)`（公钥是 base58 不是 base64）。

> **注**：这是**清单参考**，和内置的 `/security-review` 命令是两个东西 —— 为此从 `security-review` 改名而来。

### `security-scan` — 扫你自己的 `.claude/` 配置

**触发**：改过 hooks / MCP / agents 配置后，或定期体检

用 AgentShield 检查 CLAUDE.md、settings.json、MCP server 定义、hooks、agent 定义里的注入风险和错误配置 —— **AI 配置本身也是攻击面**。v1.4.0 能力齐全：`--baseline` + `--gate` 做 PR 安全门（新增 critical/high 即失败）、`--supply-chain` 校验 MCP 包来源、PreToolUse hook 做 runtime monitor 实时拦截、SARIF 输出接 GitHub code scanning。

### `plankton-code-quality` — 写时质量强制

**触发**：想要「编辑即校验」的工作流时（需先安装 Plankton）

通过 PostToolUse hook 在每次文件编辑后跑对应语言的 formatter 和 linter（biome / ruff / hadolint 等），agent 没接住的违规再起一个 Claude 子进程去修。

> **前置**：需从上游仓库手动安装 —— `github.com/alexfazio/plankton`（装之前先读一遍代码）。

---

## code-review

多语言 code review 自动分发。一条命令（`/code-review`）检测变更涉及的语言，并行调起对应的语言专家 agent，外加每次必跑的 security 审查。

**命令：**
- **`/code-review`** — 审本地未提交改动；或 `/code-review <pr>` 审 GitHub PR（拉 diff、跑校验、发布 review）

**Agent（5 个）：**
- **`code-reviewer`** — 语言专家未命中时的通用兜底
- **`python-reviewer`** — PEP 8、Pythonic 惯用法、类型注解、安全（bandit）、Django / FastAPI / Flask 模式
- **`typescript-reviewer`** — 类型安全、async 正确性、React / Next.js 模式、Node 安全
- **`swift-reviewer`** — Swift 6 并发、值类型、actor 模式、SwiftUI、Keychain / ATS 安全
- **`security-reviewer`** — OWASP Top 10、密钥检测、注入、不安全加密。**每次都会自动跑**，不论语言

---

## research

### `search-routing` — 所有联网搜索的总路由

**定位**：按查询特征选一个搜索 MCP，挑最便宜够用的。
**触发**：有多个搜索 MCP 可用时，**发起任何 web 搜索之前**

决策顺序自上而下：

0. 已知 URL → 直接抓取，不搜索（JS 重 / 付费墙 / 需渲染的走 `firecrawl_scrape`）
1. 带 `site:` / 引号等操作符、指定域名 → firecrawl（**exa 是神经检索，会忽略操作符**）
2. 中文 SERP → firecrawl（对中文搜索结果的覆盖优于 exa 的神经索引）
3. 价格 / 付费墙 / 优质出版商数据 → linkup standard（有 Statista、Xerfi 等内容授权）
4. 库和 API 文档 → **先 Context7**，返回不相关再退回 exa
5. 其余默认 exa
6. deep 模式（约 10 倍成本）**必须先问你**，并说明理由和单次价格

附成本表和实测过的 exa 工具签名（整个 server 只暴露 `web_search_exa` 和 `web_fetch_exa` 两个工具）。

> **检索心法**：第一轮搜索常常是在学项目自己的词汇 —— 搜 "rate limit" 一无所获，可能只是因为代码库里管它叫 "throttle"。

### `research` — 多源深度研究

**定位**：规划 → 采集 → 深读 → 带引用综合。使用量全库第四。
**触发**：要求深入研究某话题、要带证据和引用的报告时

先把研究问题拆开，再按场景走采集清单：

- **投资人尽调** —— 基金规模 / 阶段 / check size / portfolio / 红旗
- **竞品分析** —— 产品实况而非营销文案、融资史、定价线索
- **市场规模** —— top-down 与 bottom-up 互相验证
- **供应商评估** —— trade-offs / lock-in / 合规

搜索用 `web_search_exa`，深读用 `web_fetch_exa` 或 `firecrawl_scrape`（JS 重 / 付费墙），最后综合成带来源引用的报告，有质量规则把关。

> **先确认后端在不在，再照着它规划。** MCP server 是按配置目录隔离的，`exa` / `firecrawl` / `linkup` 可能这个会话有、那个会话没有。现在 skill 会先检查，不在就退到内置 `/deep-research` workflow 或内置 `WebSearch`，并说明这次用的是哪条路——而不是拿着调不动的工具硬跑。

### `llm-cost-discipline` — 两层 LLM 成本控制

**触发**：构建 LLM 管道、控制 API 成本、纠结正则还是 LLM 解析结构化文本时

- **Layer 1 · 避免调用**：结构化文本先上正则解析，用固定扣分制标出低置信项 —— **只有检出原因的才升级给 LLM**，并按严重度排序以适配预算上限。有 410 条真实样本的效果数据背书。
- **Layer 2 · 让调用变便宜**：按任务体量路由模型档位（cheap / strong 双档常量），不可变 CostTracker 从 `response.usage` 实时计费。

> **定价原则**：一律现查（`claude-api` skill 或官方定价页），文档里绝不硬编码价格数字 —— 硬编码的价格半年后就是错的。

---

## skills

Skill 的自我管理。原 13 个，10 个 instinct 相关的因依赖的 CLI 和数据从未存在而删除。

### `skill-stocktake` — 审计 skill 质量

**触发**：要盘点 skill / 命令质量时

两档：Quick Scan 只看最近变更的 skill，Full Stocktake 全量过一遍；用质量清单 + 子 agent 批量评审做整体判断。`scan.sh` 从脚本自身位置推导仓库根，扫 `plugins/*/skills/*/SKILL.md` 全集。

### `skill-comply` — 验证 skill 是否真被遵守

**定位**：写了不等于生效 —— 用真实运行数据证明。
**触发**：怀疑某个 skill / rule 形同虚设时

用 `claude` CLI 跑目标场景（自动生成 3 档严格程度的 prompt），解析 stream-json 输出，配对「应触发的规则」和「实际行为」，产出带完整工具调用时间线的遵守度报告。

> **注**：是全仓库唯一自带可跑测试（uv + pytest）的 skill，stream-json 配对算法是真实集成知识。

### `rules-distill` — 从 skill 蒸馏跨切原则

**触发**：发现多个 skill 在重复讲同一条原则时

`scan-skills.sh` 扫全部 skill 提取候选原则（输出合法 JSON，实测可跑），聚类后把跨切的部分提炼成 rules 文件 —— 追加、修订或新建。`~/.claude/rules` 目录不存在时按「现有 rules 为空」处理，直接进入蒸馏，不算失败。

---

## business

### `investor-materials` — 融资材料全套

**触发**：做 pitch deck、一页纸、投资人备忘录、加速器申请、财务模型、投资人联络时

Deck 结构、一页纸、备忘录、财务模型、use-of-funds 表、里程碑计划的产出指引，并保证多份材料之间数字自洽。Outreach 小节刻意浓缩成两个硬数字：

- **跟进节奏**：day 0 首发 → day 4–5 简短跟进（**带一个新数据点**）→ day 10–12 干净收尾，然后停
- **请人转介绍**：blurb 控制在 100 词内，让对方可以直接原样转发

---

## codex

通过 Codex MCP 拿第二意见 —— read-only sandbox、approval never，**只读不改**。两个的分工：一个找 bug，一个质疑方向。

### `codex-review` — 默认代码审查入口

**触发**：说 code review / 审一下 / second opinion / 看看这次改动

通过 `mcp__codex__codex` 让另一个模型跑多语言审查方法论：严重度矩阵、`file:line` 定位、范围分诊、强制安全检查。三方路由表：

- 默认走这里 —— 要的就是**外部**第二意见
- 要发 PR 行内评论（`--comment`）或自动应用修复（`--fix`）→ 内置 `/code-review`
- 点名要 Claude 语言专家 subagent → `code-review` plugin

### `design-challenge` — 质疑方案本身

**触发**：说 质疑这个方案 / challenge this design / punch holes in this / 这个设计靠不靠谱

把已成形的方案交给 Codex 一次性攻击，返回**隐含假设 / 失败模式 / 替代方案** —— 明确不是 bug 列表，没有严重度矩阵。

> **分工**：想被逐题交互式拷问 → `grill-with-docs`；想让外部模型对一份完整方案一轮打穿 → 这个。

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
> 帮我审查这段代码安全性          # 触发 security-checklist
```

大部分 skill 通过自然语言匹配 description 自动触发 —— 上面每个 skill 的「触发」行就是它实际的匹配面。少数是**显式调用**才生效的（`caveman`、`/cpr`、`/code-review`），刻意如此。

## 依赖

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- GitHub CLI (`gh`) — `cpr` 工作流需要
- 飞书 MCP server — `feishu` skill 需要
- Codex CLI + MCP server — `codex` plugin 需要
- Python venv — `pdf` / `cheatsheet` / `ui-ux-pro-max` / `skill-comply` 的脚本需要
- 各类 API key 按 skill 不同（Exa / firecrawl / linkup / Context7 / Gemini / ElevenLabs / fal.ai 等）

## 许可证

MIT
