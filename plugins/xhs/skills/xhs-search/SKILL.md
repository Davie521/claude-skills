---
name: xhs-search
description: "搜索小红书 (Xiaohongshu) 笔记。Trigger when user says '搜小红书 X' / '小红书搜 X' / '小红书查 X' / '小红书看看 X' / 'xhs 搜 X' / 'xhs search X'. Calls the local Spider_XHS project at ~/Desktop/claude-skills/Spider_XHS to fetch top results (title, author, likes, URL, optionally full body)."
---

# 搜小红书 (xhs-search)

调用本地 `~/Desktop/claude-skills/Spider_XHS` 项目搜索小红书笔记并把结果整理给用户看。

## 触发

用户消息里出现：
- "搜小红书 <关键词>"
- "小红书搜<关键词>"、"小红书搜一下 <关键词>"
- "小红书查 <关键词>"、"小红书看看 <关键词>"
- "xhs 搜 <关键词>"、"xhs search <关键词>"
- 上下文很明显是要搜小红书时，也可以触发

## 如何执行

固定用项目的 venv 跑 `cli/search.py`。**一行命令**（必须包含 `source .venv/bin/activate`）：

```bash
cd ~/Desktop/claude-skills/Spider_XHS && source .venv/bin/activate && python cli/search.py "<关键词>" -n <数量> [其它参数]
```

### 参数

| 参数 | 默认 | 何时改 |
|---|---|---|
| `-n N` | 10 | 用户没指定数量 → **用 5**；说"多一点" → 10；说"很多" → 20 |
| `--sort 0\|1\|2\|3\|4` | 0 综合 | 用户说"最新" → 1；"最火/最多赞" → 2；"评论最多" → 3 |
| `--type 0\|1\|2` | 0 不限 | "只看视频" → 1；"只看图文" → 2 |
| `--time 0\|1\|2\|3` | 0 不限 | "最近一天" → 1；"这周" → 2；"半年" → 3 |
| `--detail` | off | 用户**明确**说要正文 / 简介 / 评论数 / 收藏数 时加；否则不加（每条会多一次详情请求，慢且容易触发风控） |

### 输出格式

stdout 是 JSON 数组，每条形如：

```json
{
  "id": "6a01a5b300000000360015fa",
  "title": "🇬🇧英国签证建议：别太相信xhs的攻略",
  "author": "签证百事通",
  "likes": "214",
  "type": "normal",
  "url": "https://www.xiaohongshu.com/explore/...?xsec_token=..."
}
```

加 `--detail` 还会有 `desc` / `comments` / `collects`。

stderr 出错时输出 `{"error": "..."}` 并 exit 非 0。

## 怎么把结果展示给用户

**默认呈现格式**（简洁版）：

```
搜到 N 条「<关键词>」相关笔记：

1. [214 赞] 🇬🇧英国签证建议：别太相信xhs的攻略
   作者：签证百事通
   https://www.xiaohongshu.com/explore/...

2. ...
```

要点：
- `likes` 字段是字符串，可能是 "214" 也可能是 "1.2w"，原样展示
- URL 整行单独一行（带 xsec_token，**xsec_token 24h 内有效**，超时要重搜）
- 用户问"哪个最值得看"——按 likes 数（注意 "1.2w" 这种）排序挑前 1-2 条扼要解释
- 用户问"这条说了啥"——再调一次 `--detail` 或对单条调 `get_note_info`

## 常见错误处理

| 错误信号 | 含义 | 怎么办 |
|---|---|---|
| stderr 含 "登录" / "权限" / "461" / "401" | cookie 过期 | 提示用户重新登录小红书取 cookie 写入 `~/Desktop/claude-skills/Spider_XHS/.env` |
| stderr 含 "COOKIES not set" | 没配 cookie | 同上 |
| stderr 含 "请求过于频繁" / "300031" | 触发风控 | 提示用户等几分钟再试，或挂代理 |
| 长时间不返回（>60s） | 网络/JS 引擎卡 | 杀掉重试，多次仍然 → 提示用户检查网络 |

## 不要做的事

- ❌ 不要用 `python -m spider.spider`（它会下载图片视频到 `datas/`）
- ❌ 不要直接装 pip 包到系统（这个项目必须用 `~/Desktop/claude-skills/Spider_XHS/.venv`）
- ❌ 不要把搜出来的 URL 当作永久链接保存——xsec_token 会过期
- ❌ 不要给用户大段贴 JSON，按上面"呈现格式"组织输出
