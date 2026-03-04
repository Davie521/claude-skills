---
name: cpr
description: "Automated Git PR workflow: detect status → commit → create PR → wait for CI → fix failures → check Copilot comments → loop until all green. Use when user says 'cpr' or wants to push code through the full PR pipeline."
---

# Git PR 工作流

自动化 PR 全流程：检测状态 → 提交 → 创建 PR → 等 CI → 修复 → 循环。

## 执行原则

1. **先检测状态再继续** — 从当前状态接续
2. **不要停下来问用户** — 每步完成后直接继续
3. **循环修复直到通过** — CI 失败 → 查错 → 修复 → 推送 → 重复
4. **完整执行** — CI 通过且无 Copilot 问题才算完成

## 状态检测

```bash
gh pr view --json number,state 2>/dev/null  # 是否已有 PR
gh pr checks                                 # CI 状态
git status                                   # 未提交更改
```

| 状态 | 操作 |
|------|------|
| 无 PR | 从创建 PR 开始 |
| CI 运行中 | 等待完成 |
| CI 失败 | 查看错误日志 → 修复 → 推送 |
| CI 通过 | 检查 Copilot 评论 |

## 流程

1. **检查分支** — 在 main 上则先创建新分支
2. **提交更改** — `git add` + `git commit`
3. **推送 + 创建 PR** — `git push -u` + `gh pr create`
4. **等待 CI** — `gh pr checks --watch`
5. **CI 失败时** — `gh run view <id> --log-failed` → 修复 → 推送
6. **Copilot 评论** — `gh pr view --comments` + `gh api repos/{owner}/{repo}/pulls/$PR_NUMBER/comments` → 修复必要问题 → 推送
7. **循环 4-6** 直到全部通过
