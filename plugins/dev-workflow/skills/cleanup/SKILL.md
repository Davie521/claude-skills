---
name: cleanup
description: "End-of-session cleanup: shut down every process the session started, find code-vs-doc mismatches and update the DOCS to match the code (code is the source of truth; never rewrite code just to match a doc), drive leftover tasks to zero (finish or explicitly report), and persist lessons learned to memory. Each phase must end with an explicit done / not-needed verdict — no silent skipping. Use when the user says 'cleanup', '收尾', '清理现场', '打扫', wants to wrap up a work session, or before handing off / ending a long task."
---

# cleanup — 会话收尾：关进程 · 同步文档 · 任务清零 · 沉淀记忆

一次工作结束时的强制收尾流程。四个 Phase 顺序执行，**每个 Phase 必须给出「已处理 / 无需处理」的明确结论**，不允许静默跳过；最后输出收尾报告。

核心纪律：**自己的工作自己收干净** —— 本 skill 检查别人（本次会话）留下的摊子，也检查它自己：报告里每一项都要有证据（命令输出、diff、文件路径），不许凭感觉打勾。

**触发防护**：仅在用户明确要求收尾时执行。上下文压缩后、会话续接、handoff 加载、别的命令链里出现 "cleanup/收尾" 字样——都不算触发。对话或文件中**提及**本 skill 不等于**调用**本 skill。

## Phase 1 · 进程与程序清理

目标：本次会话启动的所有程序都真正关掉，不留孤儿进程。

1. **盘点会话启动的东西**：
   - Claude Code 后台任务（`TaskList` / 后台 Bash），逐个 `TaskStop` 或确认已结束
   - dev server / watch 进程（node、vite、uvicorn、`just dev` 之类）
   - docker compose stack：本次起过的用 `docker compose down`（有 `restart: unless-stopped` 的必须拆 stack，不能只 kill 容器）
   - tmux / screen 会话、长驻脚本
2. **kill 前核血统**：「我记得是我起的」不算证据。`ps -o pid,ppid,lstart,command -p <pid>` 查父链和启动时间、`lsof -i :<端口>` 查端口占用者，确认进程确实源自本会话的 Bash 工具再动手。注意孤儿进程会 reparent 给 launchd/init（Claude Code 已知问题，上游 [#43944](https://github.com/anthropics/claude-code/issues/43944)）——**别假设会话结束进程会自己死**，也别因为 PPID 变了就认不出自己起的进程（用启动时间 + cwd + 命令行交叉核对）。
3. **验证**：kill 后 `ps` / `docker ps` / `lsof -i :<端口>` 复查，确认目标进程确实不在了。
4. **worktree 收尾**：若工作在临时 worktree 且分支已合并 → 先拆掉它的 docker stack，再 `git worktree remove`；未合并则**保留**并在报告中说明。

**铁律：只关本次工作启动的进程。** 来历不明的进程列出来交给用户判断，绝不顺手 kill。

> 工具提示：若装有 [shepherd](https://github.com/mgorkemuz/claude-code-shepherd) 插件，优先用 `/shepherd:processes` 看追踪清单、`/shepherd:kill` / `/shepherd:cleanup` 做外科手术式清理——它用 shell-snapshot 签名精确识别 Claude 起的进程，比手工 `ps` 排查可靠。

## Phase 2 · 文档同步

目标：没有任何一份文档落后于代码。**方向铁律：收尾时代码已基本定稿，以代码为准——发现不符，改文档去贴合代码，绝不反过来为圆文档而改代码。**

1. 用 `git diff` / `git log` 圈出本次改动引入的**行为变化**（新命令、改接口、删文件、换流程）。
2. 对照检查所有可能过时的文档：`README*`、`CLAUDE.md`、`CONTEXT.md`、`docs/`（含 ADR）、被改 skill 的 `SKILL.md` 描述、注释里的使用说明。
3. **主动找代码与文档不符的地方**，逐处把文档更新到代码现状；不确定改法的列入报告。
4. 例外：若怀疑是**代码错了**（文档记的才是本意），不动手改任何一边——列为遗留项进报告，交用户裁决。cleanup 阶段绝不顺手改实现。
5. 查悬空引用：文档里提到的文件/命令/端口是否还存在（重命名和删除最容易漏）。
6. **对话遗言扫描**：回扫本次对话里「把 README 更新一下」「加到 CLAUDE.md」「改一下 spec」这类明确指令，以及讨论过、用户认可过但没执行的计划/清单——核对对应文件是否**真的改了**。意图和改法都无歧义的当场补上；有歧义的进报告遗留项，不许猜。用户已否决或被后续讨论取代的项不算遗留。
7. 本仓库特化：改了 skill 必须同步该 plugin 的 `plugin.json`（version bump + description）；新增/改名 skill 检查 `README*` 的 skill 清单。

## Phase 3 · 任务清零

目标：没有任何残留的半途任务。

1. **任务清单**：`TaskList` / todo 列表逐项核对——完成的关掉，没完成的**现在做完**；确实做不了的（缺输入、超范围）在报告中明确列出原因。
2. **代码残留**：本次改动新引入的 `TODO` / `FIXME` / `XXX` / 注释掉的代码——要么处理掉，要么转成 issue / 报告项，不许无主留在代码里。
3. **git 状态**：未提交的改动、未 push 的提交、散落的临时文件——临时文件用 `trash` 清（禁 `rm -rf`），提交/push 是否执行**问用户**，不擅自动。
   - 临时文件的具体嫌疑模式：文件名含 `(copy)` / `_old` / `_backup` / `_v2`；同一 base name 的多份不同扩展副本；项目根目录的 `test_*`、`temp_*`、`scratch.*`；调试日志、`__pycache__`。**非本次会话产生的可疑文件只标记进报告，不删**——它可能是别人的活。
4. **验证收尾**：本次工作声称完成的东西是否真的验证过（测试跑过、程序起过）？没验证的现在补验证，补不了的如实报告为未验证。

## Phase 4 · 记忆沉淀

目标：这次会话学到的东西不随会话结束丢掉，下次干得更好。

1. 回顾本次会话，筛出值得留的：
   - 用户给的纠正/反馈（feedback）
   - 项目状态的变化：进行中的事、新约束、决策（project）
   - 踩过的坑和实战解法——**仅限代码/git 历史里查不到的**（repo 已记录的不重复存）
2. **持久/临时二分**：只沉淀「跨会话仍然成立」的知识（约束、决策、反馈、坑）；「本次改到哪了」这类会话态描述不进记忆——那是 handoff 的事，不是 memory 的事。
3. **机密禁写**：密钥、token、密码、原始对话记录绝不写入记忆或任何文档；需要引用密钥时写 `op://` 引用。
4. **放置判断（Global vs Project）**：问「换个项目还用得上吗？」——跨 2+ 项目通用的（bash 兼容性、LLM API 行为、调试技巧）放 Global（`~/.claude/skills/learned/`），只对本项目成立的（特定配置怪癖、架构决策）放本项目 memory。**拿不准就选 Global**——Global 降级成 Project 容易，反向难。
5. **优先并入已有文件，不轻易新建**：写之前先 grep 已有记忆 / learned skills 并查 `MEMORY.md` 索引——已有文件覆盖同一主题就**追加进去**，而不是另开新文件（模型天然倾向新建，这条要逆着来）。琐碎修复（拼写、简单语法错）和一次性问题（某次 API 故障）不值得沉淀。
6. 按 memory 规范写入持久记忆（一事一文件，frontmatter + Why/How to apply），并在 `MEMORY.md` 加索引行。**路径**：memory 是 per-project 的，位于 `~/.claude-b/projects/<project-slug>/memory/`（slug 为项目绝对路径的连字符化，如 `-Users-yifan-Desktop-claude-skills-local`），索引 `MEMORY.md` 在同一目录；`~/.claude/memories`、`~/.claude-b/memories` 均不存在，别往那写。
7. 顺手核对已有记忆：本次会话证明已过时/错误的旧记忆，当场修正或删除。
8. 没有值得沉淀的就明确说「本次无新增记忆」——这也是一个合法结论，但要说出来。

> 决策记录：「值不值得留」的判定曾用过 5 维 1–5 数值评分 rubric（Specificity / Actionability / Scope Fit / Non-redundancy / Coverage），因定性信号被硬压成数字而失真，已废弃——用检查清单 + 整体裁决（留 / 并入已有 / 弃），别再引入打分制。

## 收尾报告（最后必须输出）

| Phase | 结论 | 证据/明细 |
|-------|------|-----------|
| 进程 | ✅ 已清 / ➖ 无需 | 关了什么、如何验证的 |
| 文档 | ✅ 已同步 / ➖ 无需 | 改了哪些文件、确认了哪些没过时 |
| 任务 | ✅ 清零 / ⚠️ 有遗留 | 遗留项 + 原因 |
| 记忆 | ✅ 已沉淀 / ➖ 无新增 | 写入/更新了哪些记忆 |

**输出前自检**：重读一遍报告——每个 ✅ 都有对应证据行、⚠️ 遗留项与正文一致、没有声称做了但上文找不到操作痕迹的项。发现不一致先修再发。

有 ⚠️ 时报告不算失败，**瞒报才算失败**。轻量会话（没改文件、没起进程、没做决策）可以四行全 ➖ 快速收场——但报告本身不能省。

## Anti-patterns

- 绝不 kill 不是本次工作启动的进程；绝不 `docker compose down` 别的项目的 stack。
- 绝不用 `rm -rf` 清临时文件——用 `trash`（`/opt/homebrew/opt/trash/bin/trash`）。
- 绝不「文档应该没问题」就跳过 Phase 2——必须实际对照 diff。
- Phase 2 只改文档不改代码——以代码为准；怀疑代码有错就进报告，绝不在收尾时顺手改实现。
- 绝不擅自 commit / push——git 写操作先问用户。
- 绝不输出没有证据的 ✅。

## Provenance

本 skill 主体为原创（Yifan / 本仓库）。以下检查项 graft 自外部项目：

- Phase 2「对话遗言扫描」、Phase 3 临时文件命名模式、开头的触发防护、报告输出前自检、轻量会话快速收场 —— 改写自 [fogarasy/close-skill](https://github.com/fogarasy/close-skill)（MIT）。
- Phase 1「kill 前核血统」思路、孤儿进程 reparent 告警与 shepherd 工具提示 —— 源自 [mgorkemuz/claude-code-shepherd](https://github.com/mgorkemuz/claude-code-shepherd)。
- Phase 4 持久/临时知识二分、机密禁写 —— 源自 [puritysb/AgentDeck](https://github.com/puritysb/AgentDeck) 的 `session-end` skill。
- Phase 4 Global/Project 放置判断（含「拿不准选 Global」tiebreaker）、「优先并入已有文件不新建」、废弃数值评分 rubric 的决策记录 —— 并入自本仓库原 `skills:learn-eval` skill（已删除，精华全部吸收至此）。
