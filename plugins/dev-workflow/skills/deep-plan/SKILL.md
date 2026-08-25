---
name: deep-plan
description: "Restate requirements, assess risks, create a step-by-step implementation plan, and WAIT for explicit confirmation before touching any code. On approval the FIRST action MUST be creating an isolated git worktree (never edit the main worktree); implement inside it; after implementation hand off to /cpr (PR pipeline) or code review. Use when starting a feature, architectural change, complex refactor, multi-file change, or when requirements are unclear."
---

# deep-plan — 规划 + worktree 隔离 + 实现后交接

写任何代码前先复述需求、评估风险、出分阶段计划，等你明确确认；批准后第一步强制开独立 git worktree（绝不在 main 工作树改动），实现完再交接给 cpr / code review。

> 内置 `/plan` 是只读 plan mode，不建 worktree。本 skill 把规划闸门与 worktree 隔离合成一步。

## 概览
1. **Restate Requirements** — 复述要做什么
2. **Identify Risks** — 暴露隐患与阻塞
3. **Create Step Plan** — 拆成分阶段步骤
4. **Create Worktree** — 自动建隔离 git worktree（无需再问）
5. **Wait for Confirmation** — 未获批准不得继续

## 何时用
- 起一个新功能
- 重大架构改动（significant architectural changes）
- 复杂重构
- 会牵动多个文件/组件
- 需求不清或有歧义

## Phase A · 规划（只读）
1. **Analyze + restate** — 厘清并复述需求
2. **Break into phases** — 拆成具体可执行步骤
3. **Identify dependencies** — 标出组件间依赖
4. **Assess risks** — 风险与阻塞
5. **Estimate complexity** — High / Medium / Low 评级
6. 用 **Explore 子 agent** 探代码、优先找可复用的现有函数/工具（避免重造轮子）
7. 用 **Plan 子 agent** 产出实现设计（可多视角：简洁 vs 性能 vs 可维护）
8. （可选）进入内置 plan mode（`EnterPlanMode` 工具 / shift+tab）借 harness 的只读强制 + 批准闸
9. **Present the plan and WAIT** — 呈现计划，等明确确认

> 说明：上面的 Explore / Plan 子 agent 与 `EnterPlanMode` 均为 Claude Code **内置 plan mode 能力，无需安装任何外部 agent**。

### 确认闸 — 不可弱化
**CRITICAL：未得到 "yes" / "proceed" / "确认" 之前，绝不写任何代码。**
要改计划，用：
- `modify: [改动]`
- `different approach: [替代方案]`
- `skip phase 2 and do phase 3 first`

## Phase B · 建 worktree（铁律：批准后、动任何代码前）
1. **命名**——请求 → `<slug>`（非 ASCII 转短英文 slug）。目录 `../<repo>_<slug>`，分支 `plan-<slug>`，两者一一对应，不要各起各的。

2. **判断当前处境**。`--show-toplevel` 判不出主树还是链接树（两种情况都只返回一个路径）。要比 git-dir 与 common-dir，**且必须加 `--path-format=absolute`**：

   ```bash
   G=$(git rev-parse --path-format=absolute --git-dir 2>/dev/null)
   C=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)
   if   [ -z "$G" ];      then echo NOT_A_REPO
   elif [ "$G" = "$C" ];  then echo MAIN
   else echo "LINKED: $(git rev-parse --show-toplevel)"; fi
   ```

   > **不加 `--path-format=absolute` 这个判断是错的。** 不加时 git 返回的两个路径格式不一致——在仓库子目录里 `--git-dir` 给绝对路径而 `--git-common-dir` 给相对路径（实测 git 2.50.1：`/abs/repo/.git` vs `../../.git`），字符串比较失败，**主工作树被误判成 LINKED**。agent 经常先 `cd` 进子目录再执行，踩中率很高。

   三种输出的处置：
   - `NOT_A_REPO` —— 先 `git init` 并做一个初始 commit，再往下走（第 3 步的 `BASE` 会是空，走 off-HEAD 分支）。
   - `MAIN` —— 在主工作树，**必须建树**，走第 3 步。
   - `LINKED: <路径>` —— **不等于可以直接开工**。确认这棵树是不是为「本次计划」建的：路径尾巴是 `_<slug>`、分支是 `plan-<slug>` 才算数。是则跳到 Phase C；**若是别的任务的树，照样要为本次计划另建一棵**，否则两份互不相干的改动会混进同一个分支和同一个 PR。

3. **建树**。base ref 探测和 `git worktree add` 必须在**同一次 shell 调用里**完成——`BASE` 是 shell 变量，跨工具调用不保留，分两次跑第二次拿到的是空串，`git worktree add ... ""` 会 `fatal: invalid reference`：

   ```bash
   git fetch origin 2>/dev/null                                  # 有 remote 才有意义
   git remote set-head origin -a >/dev/null 2>&1                 # origin/HEAD 常没设，先补（注意：这会写一个 ref）
   BASE=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)
   # 网络不通时上面全哑火，但本地 remote-tracking ref 往往还在，别直接退到 HEAD：
   [ -z "$BASE" ] && for b in origin/main origin/master; do
       git rev-parse --verify -q "$b" >/dev/null && BASE=$b && break
   done
   if [ -n "$BASE" ]; then
       git worktree add ../<repo>_<slug> -b plan-<slug> "$BASE"
   else
       git worktree add ../<repo>_<slug> -b plan-<slug>          # off 当前 HEAD
   fi
   ```

   要点：
   - `git symbolic-ref` 在 origin/HEAD 未设置时是 **fatal 而不是空输出**，所以 `set-head` 那行不能省。
   - 两条 `worktree add` **互斥**，用 `if` 保证只跑一条；写成两行并列的话 agent 会两条都执行。
   - `BASE` 最终为空（无 remote / 空仓 / 离线且没有 remote-tracking ref）就 off 本地 HEAD，此时**必须明说这次基线是本地 HEAD 而不是 origin**，别让人以为是最新 main。
   - 空仓（`git init` 后无任何 commit）走 else 分支——git ≥ 2.50 会自动推 `--orphan`；带 base ref 那条会失败。

4. 默认建**兄弟目录**：`EnterWorktree` 建在主仓 `.claude/worktrees/` 里的嵌套树，bind-mount 整个源码树的 docker dev stack 用不了。没有 docker 依赖的简单仓库可以退而用 `EnterWorktree`（默认 off `origin/<default>`，除非把 `worktree.baseRef` 设成了 `head`）。

5. `cd` 进去，播报路径 + base ref（如 "worktree: `../moneytalk_add-podcast` off `origin/main`"）。一切代码改动都在树内。

### 目标仓库若自带 worktree bootstrap
建树后先找仓库自己的隔离栈脚本（`Justfile` / `bin/init-worktree.sh` / `Makefile` / `docs`、`infra` 里的 multi-worktree 章节），有就用它，别手工配端口。

- 收尾顺序固定：**先拆 docker stack，再删目录**。`restart: unless-stopped` 的容器会不断重建被删掉的挂载点，直接 `rm` 目录只会留下一堆空壳。正确顺序是 stack teardown → `git worktree remove`。
- 已知实例：MoneyTalk `web_new` —— `just dev` 按 slot 分配端口（3000/8000/5433+slot）并软链 `backend/.env`，收尾 `just wipe` → `git worktree remove`，细节见该仓 `infra/LOCAL_DEV.md` §4「Multi-worktree dev」。

## Phase C · 实现
仅在该 worktree 内实现；绝不在 main 工作树落代码。

## 实现后 · 交接
实现 + 自测通过后，主动引导继续：
- **`/cpr`** — Git PR 全流程：提交 → 建 PR → 等 CI → 修复 → 批判性处理 Copilot 评论 → 循环至全绿 →（CI 过后自动合并；review 未过则暂停并通知）。
- **code review** — `/code-review`（多语言 + 强制安全审查）或 `codex` 的 codex-review 独立复审；关键产物可 `/quality:santa-method` 双 reviewer 对抗式验证。

## 示例
```
User: /dev-workflow:deep-plan I need to add real-time notifications when markets resolve

Agent:
# Implementation Plan: Real-Time Market Resolution Notifications

## Requirements Restatement
- Send notifications to users when markets they're watching resolve
- Support multiple notification channels (in-app, email, webhook)
- Ensure notifications are delivered reliably
- Include market outcome and user's position result

## Implementation Phases

### Phase 1: Database Schema
- Add notifications table with columns: id, user_id, market_id, type, status, created_at
- Add user_notification_preferences table for channel preferences
- Create indexes on user_id and market_id for performance

### Phase 2: Notification Service
- Create notification service in lib/notifications.ts
- Implement notification queue using BullMQ/Redis
- Add retry logic for failed deliveries
- Create notification templates

### Phase 3: Integration Points
- Hook into market resolution logic (when status changes to "resolved")
- Query all users with positions in market
- Enqueue notifications for each user

### Phase 4: Frontend Components
- Create NotificationBell component in header
- Add NotificationList modal
- Implement real-time updates via Supabase subscriptions
- Add notification preferences page

## Dependencies
- Redis (for queue)
- Email service (SendGrid/Resend)
- Supabase real-time subscriptions

## Risks
- HIGH: Email deliverability (SPF/DKIM required)
- MEDIUM: Performance with 1000+ users per market
- MEDIUM: Notification spam if markets resolve frequently
- LOW: Real-time subscription overhead

## Estimated Complexity: MEDIUM
- Backend: 4-6 hours
- Frontend: 3-4 hours
- Testing: 2-3 hours
- Total: 9-13 hours

**WAITING FOR CONFIRMATION**: Proceed with this plan? (yes/no/modify)
```

## 实现机制
规划由 **Claude Code 内置 plan mode 的 Explore + Plan 子 agent** 实现（内置能力，无需安装任何 agent 文件）。

## Anti-patterns
- 规划类任务绝不在 main 工作树实现。
- 绝不跳过建树直接动代码。
- 未获确认绝不写码。

---

_吸收自本仓已移除的 `commands/plan.md`（该文件从未被加载生效）。原文依赖的 ECC `planner` agent 由内置 Explore + Plan 子 agent 等价取代；原文的 `/tdd` 交接改为 `/cpr` / code review。_
