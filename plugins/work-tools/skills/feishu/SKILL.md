---
name: feishu
description: "Feishu (Lark) MCP integration: send messages, create groups, import/read documents, query users. No file upload/download and no direct cloud-doc editing (official lark-mcp limitations). Use when user mentions '飞书'/Feishu/Lark, or asks to send a message to a Feishu group or user, create a Feishu group, import or read a Feishu doc, or look up Feishu contacts. Requires the 'feishu' MCP server (official lark-mcp CLI, tools like mcp__feishu__im_v1_*) to be configured — if its tools are absent, tell the user to configure it instead of guessing."
---

# 飞书 MCP

使用飞书 MCP Server 进行消息、群组、文档（导入/读取）操作。

## 前置条件

需要已配置名为 `feishu` 的 MCP server（官方 `lark-mcp` CLI，stdio 方式，工具名形如 `mcp__feishu__im_v1_message_create`）。若当前会话没有这些工具，先提示用户配置，不要凭空调用。

## 用户 Open ID

Configure your team's Open IDs in your project's CLAUDE.md or as environment variables.

## 能力边界（官方 lark-mcp 自己声明的，别答应做不到的事）

- lark-mcp 目前是 **Beta**，接口可能变动
- **不支持文件上传/下载**（README 原话："File upload and download operations are not yet supported"）——用户要传文件时直说做不到，请其走飞书客户端手动操作
- **不支持直接编辑云文档**：文档只有**导入（import）和读取**两种操作，不能在线改内容

## 操作模式

- **创建群组**: 指定 `owner_id` 为用户 Open ID
- **文档**: 仅导入/读取（见上）；导入时使用 `useUAT: true` 让用户成为所有者
- **查找用户**: 通过 `im_v1_chatMembers_get` 获取 Open ID
- **发送消息**: `receive_id_type: "open_id"`, `msg_type: "text"`, `content: "{\"text\":\"消息\"}"`
