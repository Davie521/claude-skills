---
name: feishu
description: "Feishu (Lark) MCP integration: send messages, create groups, create documents, upload files, query users. Use when user mentions '飞书' or any Feishu/Lark operations."
---

# 飞书 MCP

使用飞书 MCP Server 进行消息、群组、文档、文件操作。

## 用户 Open ID

| 姓名 | Open ID |
|------|---------|
| 姜奕帆 | `ou_ff448e11e249b1c458329e0f32c16b25` |
| 朱轩宇 | `ou_a09f4460d13fb8d914e97512816edd68` |
| 陈朝阳 | `ou_5aab72810b2750cba9efe3e152f02047` |
| 孙力 | `ou_8fd2ff9466f0f239ceea8c7d06593bc9` |
| 顾宇 | `ou_f176d9fe6073ba216d5dbdc3de05f74e` |

## 操作模式

- **创建群组**: 指定 `owner_id` 为用户 Open ID
- **创建文档**: 使用 `useUAT: true` 让用户成为所有者
- **查找用户**: 通过 `im_v1_chatMembers_get` 获取 Open ID
- **发送消息**: `receive_id_type: "open_id"`, `msg_type: "text"`, `content: "{\"text\":\"消息\"}"`
