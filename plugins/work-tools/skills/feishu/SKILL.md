---
name: feishu
description: "Feishu (Lark) MCP integration: send messages, create groups, create documents, upload files, query users. Use when user mentions '飞书'/Feishu/Lark, or asks to send a message to a Feishu group or user, create a Feishu doc/group, or look up Feishu contacts. Requires the 'feishu' MCP server (official lark-mcp CLI, tools like mcp__feishu__im_v1_*) to be configured — if its tools are absent, tell the user to configure it instead of guessing."
---

# 飞书 MCP

使用飞书 MCP Server 进行消息、群组、文档、文件操作。

## 前置条件

需要已配置名为 `feishu` 的 MCP server（官方 `lark-mcp` CLI，stdio 方式，工具名形如 `mcp__feishu__im_v1_message_create`）。若当前会话没有这些工具，先提示用户配置，不要凭空调用。

## 用户 Open ID

Configure your team's Open IDs in your project's CLAUDE.md or as environment variables.

## 操作模式

- **创建群组**: 指定 `owner_id` 为用户 Open ID
- **创建文档**: 使用 `useUAT: true` 让用户成为所有者
- **查找用户**: 通过 `im_v1_chatMembers_get` 获取 Open ID
- **发送消息**: `receive_id_type: "open_id"`, `msg_type: "text"`, `content: "{\"text\":\"消息\"}"`
