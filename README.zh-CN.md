# Claude Skills

[English](README.md) | **中文**

一组 Claude Code 插件，涵盖开发工作流自动化、写作辅助和生产力工具。

## 插件

### dev-workflow

Claude Code 自动化开发工作流。

#### `/cpr` — Git PR 流水线

一条命令，从本地改动到 PR 就绪。Claude 自动完成：

1. 检测当前 git 状态（未提交的更改、已有 PR、CI 状态）
2. 提交并推送代码，通过 `gh` 创建 PR
3. 用 `gh pr checks --watch` 监听 CI 检查
4. CI 失败：读取错误日志 → 修复代码 → 重新推送
5. CI 通过：审查 Copilot 评论，修复真正的问题（忽略误报）
6. 循环步骤 3-5，直到全部通过

无需人工干预 — 输入 `/cpr` 然后该干嘛干嘛。

#### `/cl` — Copilot Lint 审查

专注于 CI + Copilot 代码审查的工作流。与 `/cpr` 不同，不会创建 PR — 只审查已有的：

- 检查 CI 状态，本地修复 build/lint 错误
- 拉取 PR 上的 Copilot 审查评论
- **批判性评估每条建议** — 只修复真正的 bug、安全问题和有实际收益的改进
- 忽略过度防御的建议、误报和纯风格偏好
- 循环直到 CI 通过且所有有效评论已处理

#### `/impl` — 多 Agent 协作实现

为大型功能编排一支专业 Agent 团队：

| 阶段 | Agent | 做什么 |
|------|-------|--------|
| 0 | **Planner** | 在 plan mode 中进行 2-3 轮计划迭代，写代码前充分规划 |
| 1 | **Implementer** | 在隔离的 git worktree 中按计划编写代码 |
| 2 | **Reviewer** | 对照计划、编码规范、安全性、无障碍性进行代码审查 |
| 3 | **Tester** | 运行测试、Playwright 截图、当场修复 bug |
| 4 | **Reviewer** | 最终审查测试修复 |
| 5 | **收尾** | 整理 commit 历史，创建 feature 分支和 PR |

每个 Agent 完成 → 审查 → 修复问题 → 下一个 Agent 启动。

#### `browser` — 浏览器 MCP 路由

根据你的意图自动选择合适的浏览器工具：

| 意图 | 选择的 MCP |
|------|-----------|
| 浏览网页、填表、打开页面 | **browser-use**（Agent Browser） |
| 性能分析、调试、网络请求、console | **Chrome DevTools** |
| E2E 测试、全流程测试 | **Playwright** |

---

### writing

#### `vibe-writing` — AI 写作助手

四阶段协作写作流程，你主导，AI 辅助：

| 阶段 | 触发词 | 做什么 |
|------|--------|--------|
| **学习** | 默认入口 | 苏格拉底式对话 — AI 提出深度问题，每 4 轮生成知识卡片（核心观点 + 论据 + 金句） |
| **结构** | 说 "结构" | 汇总卡片，提供 2-3 种文章结构（问题-方案、对比、递进、故事、清单、SCQA） |
| **写作** | 说 "写作" / "迭代" | 说 "整理" 整合内容，说 "润色" 事实核查 + 语言优化 |
| **成稿** | 说 "成稿" | 串联所有输出卡片 + 过渡段落 + 开头结尾 → 完整文章 |

根据你已有的素材，可以从任意阶段开始。

---

### document

#### `cheatsheet` — A4 速查表生成器

从 Markdown 生成高密度、可打印的速查表：

- **A4 横版**，5 栏布局，6pt 字体 — 最大信息密度
- 支持 LaTeX 数学公式、表格、高亮块、注释
- 支持多页输出
- 流程：编写 Markdown → `python3 md2html.py input.md` → 打开 HTML → 导出 PDF

---

### work-tools

#### `feishu` — 飞书集成

通过 MCP Server 操作飞书：

- 发送消息给用户或群组
- 创建群聊
- 创建和编辑文档
- 上传文件
- 查询用户信息

需要配置飞书 MCP Server。

## 安装

通过 Claude Code CLI 安装各插件：

```bash
# 安装各插件
claude plugins add Davie521/claude-skills dev-workflow
claude plugins add Davie521/claude-skills writing
claude plugins add Davie521/claude-skills document
claude plugins add Davie521/claude-skills work-tools
```

## 使用

安装后，在 Claude Code 中直接输入命令：

```
> /cpr          # 推送代码走完整 PR 流水线
> /cl           # 审查并修复 Copilot lint 评论
> /impl         # 多 Agent 协作实现
> 帮我写一篇关于...的文章   # 触发 vibe-writing
> 做一张...的速查表        # 触发 cheatsheet
```

## 依赖

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- GitHub CLI (`gh`) — cpr/cl 工作流需要
- 浏览器 MCP Server — browser skill 需要（见 skill 文档）
- 飞书 MCP Server — feishu skill 需要

## 许可证

MIT
