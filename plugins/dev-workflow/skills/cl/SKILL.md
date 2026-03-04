---
name: cl
description: "Copilot Lint review workflow: check CI status → run local lint/build → review Copilot PR comments with critical thinking → fix only necessary issues → loop. Use when user says 'cl' or wants to review and fix Copilot code review comments."
---

# Copilot Lint 检查

CI 检查 + Copilot 评论审查，只修复真正有必要的问题。

## 流程

1. **检查 CI** — `gh pr checks`
2. **CI 未通过** → 查日志 `gh run view <id> --log-failed`，本地 `npm run lint` + `npm run build`，修复
3. **CI 通过** → 查 Copilot 评论：`gh pr view --comments` + `gh api repos/{owner}/{repo}/pulls/$PR_NUMBER/comments`
4. **评论未出现** → 等 30 秒后重查

## 评估每条评论的必要性

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

修复后提交推送，循环检查直到通过。
