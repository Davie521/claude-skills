---
name: impl
description: "Agent Team implementation workflow for executing coding plans. Orchestrates Implementer, Reviewer, and Tester agents in sequence with worktree isolation. Use when: (1) user says 'impl', (2) user provides an implementation plan to execute, (3) user wants multi-agent coordinated development with review checkpoints."
---

# Agent Team 实现工作流

多 agent 分工协作：Implementer → Reviewer → Tester → Reviewer → PR。每个 agent 完成后立即审查，修复后再进入下一阶段。

## 执行原则

1. **Agent 分工** — 实现、测试、审查由不同 agent 负责
2. **逐个 Review** — agent 做完 → Reviewer 审查 → 修复 → 下一个
3. **Worktree 隔离** — Implementer 在 worktree 中工作
4. **不要停下来问用户** — 每步完成后直接继续
5. **循环直到通过** — 发现问题 → 修复 → 重新验证

---

## 阶段零：计划迭代（Plan Mode）

动手写代码前，**必须 plan mode 迭代 2-3 轮**：

| 轮次 | 目标 |
|------|------|
| **第 1 轮** | 阅读需求，探索代码库，输出粗略方案 |
| **第 2 轮** | 审视计划：过度设计？遗漏？与项目风格一致？精简步骤、调整顺序、明确文件列表 |
| **第 3 轮** | 确认每步可直接执行、依赖关系正确、完成标准清晰 → 退出 plan mode |

**计划阶段多花时间 = 实现阶段少走弯路。**

---

## 阶段一：Implementer Agent

**调度**: `Agent` 工具，`isolation: "worktree"`

**Prompt 要点**:
```
按以下计划实现所有代码变更。这是一个实现任务，请直接写代码。

## 计划
[粘贴完整计划]

## 项目上下文
- 项目结构：[关键目录]
- 编码规范：[CLAUDE.md 关键规则]
- 现有模式：[参考文件路径]

## 要求
1. 先读后改 — 修改文件前先 Read 它
2. 按依赖顺序实现（后端 → 类型 → 组件 → 页面）
3. 完成后运行 build 验证无编译错误
4. 返回：变更文件列表 + 每个文件的变更摘要
```

完成后 → 合并 worktree 变更到当前分支。

---

## 阶段二：Review 实现

**调度**: `Agent` 工具，`subagent_type: "superpowers:code-reviewer"`

**审查重点**: 计划对齐、编码规范、Bug/边界、无障碍性、安全性。返回 Critical / Important / Suggestion 分级报告。

**修复规则**:
| 级别 | 处理 |
|------|------|
| Critical | 必须立即修复 |
| Important | 本次 PR 中修复 |
| Suggestion | 评估是否值得，不过度工程化 |

修复后运行 build 验证。提交：`feat: 实现描述` + `fix: address implementation review`。

---

## 阶段三：Tester Agent

**调度**: 主 context 使用 `Agent` 工具（需要浏览器 MCP）

**测试清单**:

| 范围 | 测试项 |
|------|--------|
| 后端 | pytest、curl 验证端点、边界测试（空参数/无效参数） |
| 前端 | `npm run build`、Playwright 截图、交互元素点击、错误场景、移动端视口、console 错误 |

**要求**: 发现 bug 立即修复代码（不要只报告），修复后重新验证，返回测试报告表格。

完成后提交：`fix: issues found during testing`。

---

## 阶段四：Review 测试修复

再次调用 `superpowers:code-reviewer`，审查 Tester 的修复。确认修复正确、无新问题、测试覆盖完善。

修复后提交：`fix: address testing review`。

---

## 阶段五：收尾

1. **Commit 历史**（最多 4 个）：`feat:` → `fix: review` → `fix: testing` → `fix: testing review`
2. 创建 feature 分支 → 推送 → 创建 PR
3. **绝不直接 push main**

## 完成标准

- [ ] 计划经过 2-3 轮迭代
- [ ] Implementer 完成所有变更
- [ ] Reviewer #1 的 Critical/Important 已修复
- [ ] Tester 测试全部通过
- [ ] Reviewer #2 的 Critical/Important 已修复
- [ ] PR 已创建
