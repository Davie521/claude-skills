---
name: cpr
description: "Automated Git PR workflow: detect status → commit → create PR → wait for CI → fix failures → review Copilot comments critically → loop until all green → auto-merge. Use when user says 'cpr' or 'cl', wants to push code through the full PR pipeline, or wants to review and fix Copilot code review comments."
---

# Git PR 工作流

自动化 PR 全流程：检测状态 → 提交 → 创建 PR → 等 CI → 修复 → 循环 → 合并。

## 执行原则

1. **先检测状态再继续** — 从当前状态接续
2. **不要停下来问用户** — 每步完成后直接继续
3. **循环修复直到通过** — CI 失败 → 查错 → 修复 → 推送 → 重复
4. **完整执行** — CI 通过（或确认该仓库无 CI）、Copilot 问题处理完、合并完成才算结束

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
| **仓库没有 CI** | **跳过第 4-5 步，直接进第 6 步** |
| 全绿且评论已处理 | 自动合并 |

**先分清「CI 失败」和「没有 CI」**：`gh pr checks` 在两种情况下都返回**退出码 1**——
有检查但失败时列出失败项；仓库没配 workflow 时输出 `no checks reported on the '<branch>' branch`。
后者不是失败，别拿它去 `gh run view --log-failed` 捞日志（也捞不到），更不能因此阻塞合并。
用 `ls .github/workflows/` 一眼就能确认这个仓库到底有没有 CI。

## 流程

1. **检查分支** — 在 main 上则先创建新分支
2. **提交更改** — `git add` + `git commit`
3. **推送 + 创建 PR** — `git push -u` + `gh pr create`
4. **等待 CI** — `gh pr checks --watch`；输出 `no checks reported` 即本仓库无 CI，跳到第 6 步
5. **CI 失败时** — `gh run view <id> --log-failed` → 修复 → 推送
6. **Copilot 评论** — 先确认审查已被请求（见下），再拉评论：`gh pr view --comments` + `gh api repos/{owner}/{repo}/pulls/$PR_NUMBER/comments` → 按下表评估 → 只修必要问题 → 推送
7. **循环 4-6** 直到全部通过
8. **自动合并** — 全部检查通过且无未处理 review → `gh pr merge --merge --delete-branch`；若有 review 请求变更或未通过 → 暂停合并并通知用户

## 请求 Copilot 审查

**别假设审查会自动触发**——很多仓库不会，同一个仓库也可能时有时无（本仓库 PR #1 有、#2/#3 没有）。
先看是否已请求或已审：`gh pr view <N> --json reviewRequests,reviews`。没有就手动请求：

```bash
gh api repos/{owner}/{repo}/pulls/<N>/requested_reviewers -X POST \
  -f 'reviewers[]=copilot-pull-request-reviewer[bot]'
```

**只有带 `[bot]` 后缀的 slug 能成**：`gh pr edit --add-reviewer Copilot`（或 `@copilot`）报 `'Copilot' not found`；
不带 `[bot]` 的裸 slug 报 422 `Reviews may only be requested from collaborators`。

请求后评论要 **2-3 分钟**才出现。按 20 秒一轮询、上限 10 次；
别只等一次 30 秒就断定「没有评论」——那是把还没写完的审查当成没有审查。

**回复行内评论**走 `.../comments/<comment_id>/replies`。body 里带反引号或引号时，
`-f body=...` 会被 shell 转义炸成 EOF 错误；写进 JSON 文件用 `--input` 才稳。

## 评估每条 Copilot 评论的必要性

**不要盲目修改所有 Copilot 建议！**

| 必须修改 | 可以忽略 |
|----------|----------|
| SQL注入、XSS、敏感信息泄露 | 过度防御的建议 |
| 实际会导致问题的 Bug | 假阳性、误报 |
| 严重影响可读性的风格问题 | 纯粹的风格偏好 |
| 明显的性能问题 | 微优化、过早优化 |
| 有实际收益的改进 | 教条式建议 |

**判断标准**: 当前上下文是否真有问题？修改有实际收益？符合项目需求？

输出决策：`需要修改: [原因]` / `忽略: [原因]`
