---
name: deep-plan
description: "Restate requirements, assess risks, create a step-by-step implementation plan, and WAIT for explicit confirmation before touching any code. On approval the FIRST action MUST be creating an isolated git worktree (never edit the main worktree); implement inside it; after implementation hand off to /cpr (PR pipeline) or code review. Use when starting a feature, architectural change, complex refactor, multi-file change, or when requirements are unclear."
---

# deep-plan — 规划 + worktree 隔离 + 实现后交接

写任何代码前先复述需求、评估风险、出分阶段计划，等你明确确认；批准后第一步强制开独立 git worktree（绝不在 main 工作树改动），实现完再交接给 cpr / code review。吸收自原 `commands/plan.md`（已移除）。

> 背景：内置 `/plan` 是只读 plan mode 但不建 worktree；原 `commands/plan.md` 未被加载从未生效。本 skill 二者合一并补强。

## 概览（原 plan.md「What This Command Does」）
1. **Restate Requirements** — 复述要做什么
2. **Identify Risks** — 暴露隐患与阻塞
3. **Create Step Plan** — 拆成分阶段步骤
4. **Create Worktree** — 自动建隔离 git worktree（无需再问）
5. **Wait for Confirmation** — 未获批准不得继续

## 何时用（原 plan.md「When to Use」）
- 起一个新功能
- 重大架构改动（significant architectural changes）
- 复杂重构
- 会牵动多个文件/组件
- 需求不清或有歧义

## Phase A · 规划（只读；覆盖原 plan.md「How It Works」全部步骤）
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

### 确认闸（原 plan.md「Important Notes」）— 不可弱化
**CRITICAL：未得到 "yes" / "proceed" / "确认" 之前，绝不写任何代码。**
要改计划，用：
- `modify: [改动]`
- `different approach: [替代方案]`
- `skip phase 2 and do phase 3 first`

## Phase B · 建 worktree（铁律：批准后、动任何代码前；原 plan.md「How It Works」第 6 步全部子条）
1. 先 `git rev-parse --show-toplevel` 确认**不在 main 工作树**；在的话必须先建树。
2. slug：请求 → `plan-<slug>`（非 ASCII → 短英文 slug）；若非 git 仓库则 `git init`。
3. 有 remote 则 `git fetch origin`；默认分支 `git symbolic-ref --short refs/remotes/origin/HEAD`。
4. 默认 `git worktree add ../<repo>_<slug> -b <branch> origin/<default-branch>` 建兄弟目录并 `cd` 进去（`EnterWorktree` 建在主仓 `.claude/worktrees/` 内的嵌套树，docker bind-mount 源码树的 dev stack 用不了，LOCAL_DEV.md §4 也约定兄弟目录）；无 docker 依赖的简单仓库可退而用 `EnterWorktree`（off 最新 main）。（原 plan.md 通用写法 `git worktree add ../<name> -b <name>`，此处按本仓约定本地化为 `../<repo>_<slug>`。）
5. 播报路径 + base ref（如 "worktree: `../moneytalk_add-podcast` off `origin/main`"）。一切代码改动都在树内。

### 本仓特化（MoneyTalk web_new）
- 仓库有 `bin/init-worktree.sh` + `Justfile` → 建树后 `just dev` 自动 bootstrap 隔离栈（端口 3000/8000/5433+slot、软链 `backend/.env`）；收尾 `just wipe` → `git worktree remove`。以上见 `infra/LOCAL_DEV.md` §4「Multi-worktree dev」。
- 运维经验：删 worktree 目录前先拆它的 docker stack（`restart:unless-stopped` 会不断重建空壳目录），别直接删目录——即按 §4「Tearing down」的 `just wipe` → `git worktree remove` 顺序走。

## Phase C · 实现
仅在该 worktree 内实现；绝不在 main 工作树落代码。

## 实现后 · 交接
实现 + 自测通过后，主动引导继续：
- **`/cpr`** — Git PR 全流程：提交 → 建 PR → 等 CI → 修复 → 批判性处理 Copilot 评论 → 循环至全绿 →（CI 过后自动合并；review 未过则暂停并通知）。
- **code review** — `/code-review`（多语言 + 强制安全审查）或 `codex` 的 codex-review 独立复审；关键产物可 `/quality:santa-method` 双 reviewer 对抗式验证。

## 示例（原 plan.md「Example Usage」，原文完整保留）
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

## 实现机制（原 plan.md「Related Agents」，现代化 + 原文旁注）
规划由 **Claude Code 内置 plan mode 的 Explore + Plan 子 agent** 实现（内置能力，无需安装任何 agent 文件）。
> 旁注（原 plan.md 原文，当前环境未安装）："This command invokes the `planner` agent provided by ECC. For manual installs: `agents/planner.md`." —— 已由上面的内置子 agent 等价取代。
> 旁注（原 plan.md「Integration」原文）："After planning: Use `/tdd` to implement with test-driven development." —— `/tdd` 当前未安装，实现后改走上面的 `/cpr` / code review。

## Anti-patterns
- 规划类任务绝不在 main 工作树实现。
- 绝不跳过建树直接动代码。
- 未获确认绝不写码。
