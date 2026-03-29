---
name: feishu
description: "Feishu (Lark) MCP integration: send messages, create groups, create documents, upload files, query users. Use when user mentions '飞书' or any Feishu/Lark operations."
---

# 飞书 MCP

使用飞书 MCP Server 进行消息、群组、文档、文件操作。

## 用户 Open ID

Configure your team's Open IDs in your project's CLAUDE.md or as environment variables.

## 操作模式

- **创建群组**: 指定 `owner_id` 为用户 Open ID
- **创建文档**: 使用 `useUAT: true` 让用户成为所有者
- **查找用户**: 通过 `im_v1_chatMembers_get` 获取 Open ID
- **发送消息**: `receive_id_type: "open_id"`, `msg_type: "text"`, `content: "{\"text\":\"消息\"}"`
