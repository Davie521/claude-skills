---
name: browser
description: "Browser MCP routing guide: automatically select the right browser tool (Agent Browser for browsing/form-filling, Chrome DevTools for performance/debugging, Playwright for E2E testing) based on user intent. Use when user mentions browsing, performance analysis, debugging, or testing web pages."
---

# Browser MCP 路由

根据场景自动选择合适的浏览器 MCP。

## 路由规则

| 触发词 | MCP | 工具前缀 |
|--------|-----|----------|
| 看看、填表、打开网页、浏览 | Agent Browser (browser-use) | `mcp__browser-use__*` |
| 性能、调试、网络请求、console、devtools | Chrome DevTools | `mcp__chrome-devtools__*` |
| 测试、跑全流程、E2E、端到端 | Playwright | `mcp__playwright__*` |

## 安装

```bash
claude mcp add browser-use -s user -- uvx --from browser-use[cli] browser-use --mcp
claude mcp add chrome-devtools -s user -- npx chrome-devtools-mcp@latest
claude mcp add playwright -s user -- npx @playwright/mcp@latest
```
