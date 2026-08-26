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
| **确认无 CI**（见下） | **跳过第 4-5 步，直接进第 6 步** |
| 全绿且评论已处理 | 自动合并 |

**先分清「CI 失败」和「没有 CI」**：`gh pr checks` 在两种情况下都返回**退出码 1**——
有检查但失败时列出失败项；仓库没配 workflow 时输出 `no checks reported on the '<branch>' branch`。
后者不是失败，别拿它去 `gh run view --log-failed` 捞日志（也捞不到），更不能因此阻塞合并。

**退出码 8 是「检查进行中」**，和失败的 1 不是一回事——别把还在跑的 CI 当成挂了就去改代码。

不过 `no checks reported` 只说明**这个 head commit 没有 check run**，不等于仓库没有 CI——
也可能 workflow 存在但没配到这个分支/事件上。所以要落实一下再决定跳不跳：

```bash
[ -d .github/workflows ] && echo "有 workflow 目录，属于配置问题" || echo "确实没有 CI，可跳过第 4-5 步"
```

（别用 `ls .github/workflows/`：目录不存在时它自己就非零退出并往 stderr 打错误，
在状态机里又变成一个假的「步骤失败」——正是这一步想避免的毛病。）

## 流程

1. **检查分支** — 在 main 上则先创建新分支
2. **提交更改** — `git add` + `git commit`
3. **推送 + 创建 PR** — `git push -u` + `gh pr create`
4. **等待 CI** — `gh pr checks --watch`；输出 `no checks reported` 时按上面的办法确认无 CI，是则跳到第 6 步
5. **CI 失败时** — `gh run view <id> --log-failed` → 修复 → 推送
6. **Copilot 评论** — 先确认审查已被请求（见下），再拉评论：`gh pr view --comments` + `gh api repos/{owner}/{repo}/pulls/$PR_NUMBER/comments` → 按下表评估 → 只修必要问题 → 推送
7. **循环 4-6** 直到全部通过
8. **自动合并** — 全部检查通过且无未处理 review → `gh pr merge --merge --delete-branch`；若有 review 请求变更或未通过 → 暂停合并并通知用户

## 请求 Copilot 审查

**别假设审查会自动触发**——很多仓库不会，同一个仓库也可能时有时无（本仓库 PR #1 有、#2/#3 没有）。
先看是否已请求或已审：`gh pr view <N> --json reviewRequests,reviews`。没有就手动请求：

**gh ≥ 2.88.0（2026-03-11）起有官方支持**，优先用它：

```bash
gh pr edit <N> --add-reviewer @copilot     # 或建 PR 时 gh pr create --reviewer @copilot
```

先确认版本：`gh --version`。低于 2.88.0 时这条会报 `'Copilot' not found`——
那不是语法写错，是 CLI 太旧，走 API 兜底：

```bash
gh api repos/{owner}/{repo}/pulls/<N>/requested_reviewers -X POST \
  -f 'reviewers[]=copilot-pull-request-reviewer[bot]'
```

**走 API 时只有带 `[bot]` 后缀的 slug 能成**：不带 `[bot]` 的裸 slug 报 422
`Reviews may only be requested from collaborators`。

**POST 返回 200 但 `requested_reviewers` 是空数组属正常**——GitHub 立刻把请求转成进行中的审查，
这个字段随即清空。别据此判定失败又重发，以评论是否出现为准。

**别给耗时写死一个数**。Copilot 有 Lite / Balanced 两档 effort，Balanced 会路由到高推理模型
做更长的分析，两档的实际耗时差一个量级（本仓库 Lite 实测约 100 秒）。做有上限的轮询即可：
20 秒一轮、上限 15 次（约 5 分钟）。别只等一次 30 秒就断定「没有评论」——
那是把还没写完的审查当成没有审查。

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
