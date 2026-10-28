---
name: cpr
description: "Automated Git PR workflow: detect status → commit → create PR → run CI and a Codex review in parallel → fix CI failures and the review findings that need it → re-review until the review of the current HEAD passes (no CRITICAL/HIGH introduced or enlarged by the PR) → auto-merge. Stops only when a user decision is needed. Use when user says 'cpr' or 'cl', or wants to push code through the full PR pipeline."
---

# Git PR 工作流

自动化 PR 全流程：检测状态 → 提交 → 创建 PR → CI 与 Codex 审查并行 → 修复 → 再审 → 循环 → 合并。

## 执行原则

1. **先检测状态再继续** — 从当前状态接续
2. **不要停下来问用户** — 每步完成后直接继续；只有碰到下文「停下来让用户拍板」列出的情况才停
3. **循环修复直到通过** — CI 失败 → 修；Codex 审查没通过 → 修 → 再审，直到通过
4. **完整执行** — 三件事都满足才算结束：CI 通过（或确认该仓库无 CI）；最近一轮 Codex 审查审的就是当前 HEAD，并且过闸（见「处理审查结果」）；合并完成
5. **不用 Copilot 审查**（用户 2026-10-10 定）— 不请求、不等待、不处理，见末节
6. **先确认审查用得了** — 审查要 `codex` 插件（`codex:codex-review` 技能）和 `~/.local/bin/codex-run`。
   动手提交之前先 `command -v codex-run`，没有就停下告诉用户，别跳过审查直接合并
7. **gh / GitHub 出怪现象先读技能 `gh-pr-traps`** — `graphql: EOF`、update-branch 或 push 后 head SHA 不对、新提交一个检查都不触发、`gh auth status` 说没登录、OIDC 规则被拒等；合并成功与否一律以 `gh api repos/<o>/<r>/pulls/<n> --jq .merged` 为准（全局 CLAUDE.md 的 gh 一节同样常驻）

## 状态检测

```bash
gh pr view --json number,state,baseRefName,headRefOid 2>/dev/null   # PR、目标分支、远端最新提交
gh pr checks                                                         # CI 状态
git status --porcelain                                               # 有输出 = 有未提交改动
cat "$(git rev-parse --git-dir)/cpr-review-<PR号>" 2>/dev/null       # 每次起审查一行：<SHA> <目标分支> <结果目录>
```

审查记录按 PR 号分文件、每次起审查追加一行：最后一行是最近一次。已审轮数 = 记录里不同 SHA 的个数（同一个提交的重跑不算新一轮）。

| 状态 | 操作 |
|------|------|
| 无 PR | 从创建 PR 开始 |
| CI 运行中 | 等待完成 |
| CI 失败 | 查看错误日志 → 修复 → 推送 |
| 有未提交改动 | 确认是本 PR 的活、做完、提交推送，再起新一轮。之前那轮不能拿来过闸——Codex 可能读到了改了一半的文件 |
| 没有审查记录；或最后一行的 SHA ≠ HEAD；或记录的目标分支 ≠ 现在的 `baseRefName`（改过目标分支，diff 范围变了） | 起新一轮审查（第 4 步）；旧那轮若还在跑，先 `codex-run --stop <旧结果目录>` |
| 最后一行的 SHA 和目标分支都对得上，工作树干净 | `codex-run --wait <结果目录>` 取结果（已跑完的会立刻返回） |
| **确认无 CI**（见下） | 跳过第 5-6 步，审查照做 |
| CI 全绿（或确认无 CI），当前 HEAD 的审查过闸且没有要修的 | 自动合并 |

**先分清「CI 失败」和「没有 CI」**：`gh pr checks` 在两种情况下都返回**退出码 1**——
有检查但失败时列出失败项；仓库没配 workflow 时输出 `no checks reported on the '<branch>' branch`。
后者不是失败，别拿它去 `gh run view --log-failed` 捞日志（也捞不到），更不能因此阻塞合并。

**退出码 8 是「检查进行中」**，和失败的 1 不是一回事——别把还在跑的 CI 当成挂了就去改代码。

不过 `no checks reported` 只说明**这个 head commit 没有 check run**，不等于仓库没有 CI——
也可能 workflow 存在但没配到这个分支/事件上。所以要落实一下再决定跳不跳：

```bash
[ -d .github/workflows ] && echo "有 workflow 目录，属于配置问题" || echo "确实没有 CI，可跳过第 5-6 步"
```

**别改用 `gh api repos/{owner}/{repo}/actions/workflows` 的 `total_count` 来判断**——
它把 GitHub 自己的动态 workflow 也算进去。本仓库没有任何 `.github/workflows` 文件，
该接口却返回 `total_count: 2`，两条都是 `dynamic/.../copilot-pull-request-reviewer`。
按它判断会得出「有 CI」的错误结论，然后无限等一个永远不会出现的 check。

（别用 `ls .github/workflows/`：目录不存在时它自己就非零退出并往 stderr 打错误，
在状态机里又变成一个假的「步骤失败」——正是这一步想避免的毛病。）

## 流程

1. **检查分支** — 在 main 上则先创建新分支
2. **提交更改** — `git add` + `git commit`
3. **推送 + 创建 PR** — `git push -u` + `gh pr create`（别带 `--reviewer @copilot`）
4. **起 Codex 审查** — 见「Codex 审查」；起完立刻往下走，不等它
5. **等待 CI** — `gh pr checks --watch`；输出 `no checks reported` 时按上面的办法确认无 CI，是则跳过第 6 步
6. **CI 失败时** — `gh run view <id> --log-failed` 读日志、想好修法。**审查还在跑就先别改文件**（Codex 正从工作树读代码），等第 7 步拿到结果后和审查意见一起改
7. **取审查结果** — `codex-run --wait "$D"`，按「处理审查结果」逐条评估
8. **修复 → 提交 → 推送 → 回到第 4 步** — 新 HEAD 必须重新审，哪怕只改了 CI
9. **自动合并** — CI 全绿（或确认无 CI）+ 当前 HEAD 的审查过闸且没有要修的 → 合并前再核一次：
   `gh pr view <PR号> --json headRefOid,baseRefName` 两项都要和审查记录最后一行的 SHA、目标分支一致
   （审查期间可能有人推了提交，或把 PR 改指向别的分支），不一致就回第 4 步。一致再合并：
   `gh pr merge <PR号> --merge --delete-branch --match-head-commit <那个 SHA>`，把合并锁在审过的那个提交上。
   核对之后远端又变了，GitHub 会拒绝合并：同样回第 4 步，**别去掉这个参数重试**。
   合并后以 `gh api repos/<o>/<r>/pulls/<PR号> --jq .merged` 为 `true` 为准（走 REST，GraphQL 报 EOF 时也查得到；别拿命令没报错当合并成功）。`--delete-branch` 不一定把本地切回 main：
   还停在功能分支就 `git switch main && git pull --ff-only && git branch -d <分支>`
   （在另开的工作树里，main 被主树占着切不过去，就留给收尾处理）。
   PR 上有人请求变更 → 暂停合并并通知用户

## Codex 审查

先用 Skill 工具加载 `codex:codex-review`（别去硬盘上找它的文件，换台机器路径就不一样），
照它的「Invocation」节调用（`codex-run --start` 起、`--wait` 反复等，退出码 `75` = 还在跑，再调一次），
说明模板也用那里的。修不修按本技能的规则，不按它「出结果就停」那条。cpr 里这样填：

先让本地和远端的 PR 分支一致（工作树要干净）：

```bash
git fetch -q && git rev-list --left-right --count 'HEAD...@{u}'   # 左 = 只有本地有的提交数，右 = 只有远端有的
```

| 结果 | 处理 |
|---|---|
| `0 0` | 一致，往下走 |
| 左 > 0，右 = 0（本地领先） | `git push` |
| 左 = 0，右 > 0（远端领先：有人推了新提交） | `git merge --ff-only '@{u}'` 快进拉下来，别人的提交一起进这一轮审查（别推送：会被拒，也拿不到别人的提交） |
| 左右都 > 0（分叉了） | 停下问用户怎么合，**别强推** |

一致之后：

```bash
N=<PR号>
BASE=$(gh pr view ${N} --json baseRefName -q .baseRefName)
D=$(mktemp -d "${TMPDIR:-/tmp}/codex-review.XXXXXX")
gh pr diff ${N} --color never > "${D}/pr.diff"   # GitHub 按 PR 真实的目标仓库和分支算的 diff
# 用 Write 工具写 $D/prompt.md（别用 heredoc，diff 里有引号和 $）
codex-run --start "$(git rev-parse --show-toplevel)" "${D}/prompt.md" "${D}" \
  && echo "$(git rev-parse HEAD) ${BASE} ${D}" >> "$(git rev-parse --git-dir)/cpr-review-${N}"
```

- 起审查前工作树必须干净、HEAD 已推送——Codex 读的是磁盘上的文件，要和 PR 上是同一份
- diff 用 `gh pr diff` 而不是本地 `git diff origin/<base>...HEAD`：本地的 `origin/<base>` 可能过时；
  fork 里往上游提的 PR，目标根本不在 `origin`。两种情况都会把别人的提交算成本 PR 的改动。
  `gh pr diff` 报 diff 太大（GitHub 有上限）时才退回本地：先 `git fetch <目标仓库的 remote> ${BASE}`
  （fork 里一般叫 `upstream`），再 `git diff <remote>/${BASE}...HEAD > "${D}/pr.diff"`
- CONTEXT 写这个 PR 改什么、为什么（一两句）；SCOPE 写「PR #N 的全部改动，diff 在 `<$D 的绝对路径>/pr.diff`，
  需要上下文时读工作树里的文件」；PROJECT CONVENTIONS 摘仓库 CLAUDE.md 的硬规则
- **每一轮都审整个 PR，而且保持盲审**：不附自己的怀疑清单；第二轮起也不写「上一轮报了什么、怎么改的、
  哪几条判成了误报」——那是把 Claude 的判断喂给它，独立审查就不独立了
- `--wait` 用前台 Bash，`timeout: 600000`

审查跑不出结论时，按 `codex-run --wait` 的退出码处理：

| 退出码 | 处理 |
|---|---|
| `6`（运行进程没了）/ 其他崩溃 | 自动重跑一次；再失败就停下 |
| `3`（额度用完、登录失效、模型不对）/ `90` / `124`（超时） | 停下，把 wrapper 的原话转给用户 |
| `130`（被 `--stop`） | 停下 |

没有审查结论就合并，是用户要拍板的事——别自己判「CI 过了就合」。

## 处理审查结果

**过闸** = 这一轮没有范围标为 `introduced` / `enlarged` 的 CRITICAL 或 HIGH。Codex 结论是 `APPROVE` 就满足。
但它的结论规则里「有任何 CRITICAL → `BLOCK`」连 `pre-existing` 的也算：只因为原本就有的 CRITICAL 被判 `BLOCK`，
按过闸处理，那条放进最终汇报第一条。别把「结论不是 `APPROVE`」直接等同于「没过闸」，否则会在一个本 PR 修不了的问题上空转到第 5 轮。

每条发现先**核实再动手**——打开它指的 `文件:行号`，确认问题真的存在（Codex 也会误报）——
再按下表给决策，写成 `需要修改: [原因]` / `忽略: [原因]`：

| 必须修改 | 可以忽略 |
|----------|----------|
| SQL注入、XSS、敏感信息泄露 | 过度防御的建议 |
| 实际会导致问题的 Bug | 假阳性、误报 |
| 严重影响可读性的风格问题 | 纯粹的风格偏好 |
| 明显的性能问题 | 微优化、过早优化 |
| 有实际收益的改进 | 教条式建议 |

**判断标准**: 当前上下文是否真有问题？修改有实际收益？符合项目需求？

- **`introduced` / `enlarged` 的 CRITICAL / HIGH 判成「忽略」不能自己说了算**——忽略了就永远过不了闸，属于下节要停下的情形
- `pre-existing`（改动之前就有的问题）不在本 PR 修、不挡合并，写进最终汇报，建议另开 issue
- 修完一起提交、推送，回到第 4 步。**结束条件**：某一轮过闸，且这一轮评估下来没有「需要修改」的条目

## 停下来让用户拍板

只有这些情况停，其余一律接着修：

- 某条 `introduced` / `enlarged` 的 CRITICAL / HIGH 核实后认为是误报，或认为不该在本 PR 修
- 修法有取舍：产品行为、对外接口、数据迁移、钱怎么走、权限模型，或者有两种以上都说得通的改法
- 要修的问题明显超出本 PR 范围（要动别的模块、别的仓库）
- 同一个问题修过一次，下一轮又报
- 审查跑不出结论（见上表）
- 本地和远端的 PR 分支分叉了（两边各有对方没有的提交）
- 已经审了 5 轮还没过闸（轮数 = `cpr-review-<PR号>` 里不同 SHA 的个数）
- PR 上有人请求变更

停之前先把不需要拍板的修完、推上去（CI 照跑），新一轮审查等用户答复、改完再起。
停下时一条消息讲清楚：每个待决项写 Codex 原话摘要、`文件:行号`、你核实的结果和可选方案；
**只用一组编号**，方便用户按编号回复。

## 最终汇报

合并后汇报：审了几轮、每轮结论；修了哪些；忽略了哪些（各附原因）；`pre-existing` 的发现。

## Copilot

用户 2026-10-10 定：**cpr 不再用 Copilot 审查**。建 PR 别带 `--reviewer @copilot`，事后也别请求。
仓库或账号设置让 Copilot 自己审了，它的评论不处理、不回复，不算「未处理的 review」，不挡合并。
