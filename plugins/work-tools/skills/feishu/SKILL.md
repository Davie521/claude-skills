---
name: feishu
description: "Feishu (Lark) via the official lark-cli (@larksuite/cli): messages and group chats, docs, sheets, Base, drive, wiki, calendar, tasks, mail, meetings, approvals and more. Use when the user mentions '飞书'/Feishu/Lark or shares a Feishu link and the official lark-* skill for that domain is not installed, or when lark-cli needs installing, app setup or login. Loads the matching official guide on demand with `lark-cli skills read <name>` instead of preloading every domain skill."
---

# 飞书（官方 lark-cli）

用飞书官方命令行 `lark-cli` 操作飞书。它自带 20 多份官方领域说明（消息、文档、表格、日历……），**内置在二进制里、随版本更新**，用到哪个领域时现读，不必全部装成技能常驻上下文。

## 先判断走哪条路

- **按领域判断**：当前请求所属领域的官方技能（如发消息对应 `lark-im`）已经在会话里 → 直接用它。
- 那个领域没装（哪怕装了别的 `lark-*` 技能）→ 按下面流程，用 `lark-cli skills read` 现读那个领域的说明。

## 安装与登录（一次性）

1. 装命令行：`npm install -g @larksuite/cli`（安装脚本从 GitHub Releases 下载二进制，并按包内校验和核对）。`lark-cli --version` 能出版本号即可。
2. 绑定应用：`lark-cli config init --new`（默认是飞书；**国际版 Lark 用户必须加 `--brand lark`**，否则会被带到飞书的页面，先问清用户用的是哪个）。它会打印一个链接，**放后台跑**，把链接交给用户在浏览器里点「创建」，完成后命令自己退出。飞书的接口都要经过一个应用，这一步会在用户所在企业建一个自建应用并自动配好权限。
3. 登录：`lark-cli auth login --recommend`，同样放后台、把链接交给用户授权。链接 10 分钟内有效，别反复重启命令，每次重启都会让上一个链接失效。
4. 验证：`lark-cli auth status` 里 `identities.user.tokenStatus` 为 `valid` 即可。

密钥和令牌由命令行自己保管，`~/.lark-cli/config.json` 里不含明文密钥。

官方还提供 `npx @larksuite/cli@latest install` 安装向导，它会用 `npx skills add` 把官方技能装进技能目录、常驻系统提示。只想按需使用就跳过它，用本技能现读。

注意：内置说明**只含文字，不含 `scripts/`、`assets/` 目录**。说明里要求跑脚本时（比如表格的图表质量检查、幻灯片的 XML 校验），去 GitHub `larksuite/cli` 与本机 `lark-cli --version` 相同的版本标签下，取**整个 `skills/<名字>/` 目录并保持原有结构**（脚本会引入同目录的其他脚本、读上一级 `references/` 里的文件，只取单个脚本会跑不起来），或改装该领域的官方技能。

## 按需读官方说明

```bash
lark-cli skills list                                # 全部领域及说明
lark-cli skills read lark-im                        # 读某个领域的 SKILL.md
lark-cli skills read lark-doc references/<文件>.md   # 读它引用的参考文件
```

| 要做的事 | 读哪份 |
|---|---|
| 登录、权限不足、切换用户/机器人身份 | `lark-shared`（遇到认证问题先读它） |
| 发消息、群聊、聊天记录、下载聊天里的文件 | `lark-im` |
| 云文档读写 | `lark-doc` |
| 云盘文件、上传下载、导入 Word/Excel | `lark-drive` |
| 知识库 | `lark-wiki` |
| 电子表格 / 多维表格 | `lark-sheets` / `lark-base` |
| 日程、会议室、忙闲 | `lark-calendar` |
| 待办任务 | `lark-task` |
| 邮件 | `lark-mail` |
| 视频会议记录、妙记 | `lark-meeting` |
| 按名字查人 | `lark-contact` |
| 审批 | `lark-approval` |
| 命令行没封装的接口 | `lark-openapi-explorer` |

## 调用习惯

- 优先用领域下的 `+` 快捷命令：`lark-cli <领域> --help` 列出全部，例如 `lark-cli calendar +agenda`。
- 调用前看参数：`lark-cli schema <service>.<resource>.<method>`。
- 快捷命令与类型化命令都支持 `--as user|bot` 选身份、`--dry-run` 只预览不执行、`--format` 选输出格式（可选值和默认值因命令而异，比如多维表格的记录查询默认输出 ndjson 文件，用前看 `--help`）。
- 兜底裸调：`lark-cli api GET /open-apis/<路径>`。
- 每个命令的 `--help` 标了风险等级 `read` / `write` / `high-risk-write`。`high-risk-write` 要加 `--yes`，**只在用户明确确认后加**。**所有写入和删除操作，不论用哪个身份、风险等级标的是什么，执行前都先跟用户确认目标和改动内容。** 默认身份是 `auto`（由命令行自己挑）；用户身份下的写操作是以用户本人名义执行的，必要时显式加 `--as`。

## 容易误判的地方

- **`auth login` 退出码 3 不一定是失败**：个别权限被企业管理员禁止申请时也返回 3，其余权限照样授权成功，以 `lark-cli auth status` 为准。
- **登录会过期**：刷新令牌约 7 天有效，太久不用要重新 `auth login`。
- **管理类操作别为一次性需求加权限**：比如停用企业里的应用，接口要求应用有 `admin:app.enable:write` 这类企业级管理权限。给 AI 驱动的命令行应用加上，等于让它以后能停用企业里任何应用。这类一次性操作让用户去企业管理后台点。
