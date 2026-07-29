---
name: mt-upload
description: "MoneyTalk 批量上传研报 PDF：解析文件名 + 逐份读 PDF 首页双重校验（来源/标题/日期/ticker/分析师全字段 cross-check），汇总表人工确认后经 /admin/upload-pdf 上传，含 ticker→RIC 解析、晚传确认、结果分桶。Use when user wants to batch-upload research PDFs to MoneyTalk (说 mt-upload / 批量传研报 / 上传这批 PDF)。"
---

# MoneyTalk 批量上传研报（含逐份首页 double-check）

把一个文件夹（或一组）研报 PDF 批量上传到 MoneyTalk。核心承诺：
**每一份 PDF 都读首页做全字段校验，任何一行未经用户确认绝不上传。**

输入：文件夹路径或文件列表；目标环境（local / prod，不明说就问）。

## 铁律（先读）

1. **上传前必出汇总表并等用户明确确认。** 上传 prod 是外发动作，
   没有"顺手就传了"。用户没说 target 是谁，先问。
2. **每份 PDF 都要读首页**（不是只读解析失败的）——这就是本 skill
   与 web 端批量上传的区别：Claude 亲眼看过每一份的内容。
3. **公司归属歧义 = 跳过待人工。** 宁可漏传一份，绝不把 PDF 挂到
   错误的公司上。分析不出、多个候选都存在、首页与文件名 ticker
   矛盾 → 全部进「待人工」桶。ticker 是唯一"冲突即升级"的字段，
   不走下面 Step 2 的"以首页为准"。
4. **token 不落盘。** 每条命令里现取现用（local 例：把
   `TOKEN=$(just token 2>/dev/null | tail -1)` 写在同一条 bash 命令内；
   prod 取法见 Step 6），绝不写进文件、绝不 echo 全文。每次 Bash 调用
   都是全新 shell、变量不跨调用存活——所以是"每条命令重取"，
   不是"开头 export 一次"。
5. 逐字节内容不修改：不重命名、不动用户的源文件。

## 流程

### Step 1 — 收集与解析文件名

```bash
find <folder> -maxdepth 1 -iname '*.pdf'
```

文件名规范 `{Broker}-{Title}-{YYMMDD}.pdf`。解析规则（源自
web_new PR #448 的 parser.py，已有测试背书）：

- 正则：`^(?P<broker>[^-]+?)\s*-\s*(?P<title>.+)-(?P<date>\d{6})$`
  （对去掉 `.pdf` 后的主名匹配；date 按 `%y%m%d`）
- 标题里的全角替身字形反向映射：`：→:` `；→;` `，→,` `？→?`
  `（→(` `）→)` `～→-` `~→-`，映射后 strip 空格与连字符
- ticker 提取：扫描标题括号内容，
  - `^([A-Z0-9]{1,6})\.([A-Z]{1,3})$` → root + suffix（如 `MMM.US`、`9926.HK`）
  - `^\d{6}$` → 裸 A 股代码（root，无 suffix）
  - 都不匹配 → 该文件名无 ticker（首页校验阶段再找）

解析失败不是错误——标记 `unparsed`，首页读取会补齐。

### Step 2 — 逐份读首页（double-check 核心）

对**每一份** PDF（无论文件名是否解析成功）：

```
Read(file_path=<pdf>, pages="1-2")
```

从首页提取五个字段：
- **来源/broker**：抬头、logo 文字、页眉页脚的机构名
- **标题**：报告主标题（不是栏目名/系列名）
- **发布日期**：首页日期（注意美式/欧式格式歧义；研报日期通常在
  抬头附近）
- **主体 ticker**：报告分析对象的代码（注意区分"提及"与"主体"——
  同业比较表里会出现一堆无关 ticker，主体是标题/评级框里那个）
- **分析师**：署名（多人取第一作者；没有署名记空）

然后与文件名解析结果**逐字段 cross-check**：

| 情形 | 处理 |
|---|---|
| 两侧一致 | ✓ 用该值 |
| 不一致 | ⚠ **以首页为准**填入，但该行标「字段冲突」并在表格里并排展示两个值，让用户裁决 |
| 文件名缺、首页有 | 用首页值，标 ✨（内容补齐） |
| 两侧都没有 | 该字段留空，行进「待人工」 |

**三个字段不适用上表，单独处理（本地实测踩出来的坑）：**

- **source（机构）——绝不能"以首页为准"。** 首页印的是市场主体全称
  （`Citi Research`、`UBS Equities`、`BofA Securities`），滞后规则表和
  存量目录用的是另一套规范写法（`Citi`）。取首页那个 = 归一化键匹配
  不上规则 → 掉进 `DEFAULT_LAG_DAYS=30` 默认口径。**实测**：同一份
  2026-01-01 的腾讯稿，`source=Citi Research` 直接 409
  `late_upload_lag_elapsed (effective_lag_days=30)`；换成 `source=Citi`
  （规则表里 `lag_days=null` 永久豁免）立刻 201。
  正确做法：把「文件名值」和「首页值」都拿去和 **Step 4 的规则表 +
  存量目录 source** 按归一化键（NBSP→空格、折叠空白、strip、lower）比，
  **命中规则/目录的那个胜出**；两个都命中不同项、或都不命中 → 该行标
  「来源待确认」，把两个候选并排给用户挑，别自己选。
- **ticker 冲突 → 直接进「待人工」**（铁律 3），不做"以首页为准"。
- **title** — 比较前先把文件名标题尾部的 ticker 括号剥掉
  （`英伟达数据中心增长再评估(NVDA.US)` → `英伟达数据中心增长再评估`），
  否则每一行都会被误判成「标题冲突」。剥完仍不一致才算冲突；
  正常情况下首页标题更干净，用首页的。

日期特别规则：文件名日期与首页日期差 ≤3 天视为一致（取首页值）；
差得多才算冲突（常见原因：文件按下载日命名）。

批次大（>25 份）时可用并行 subagent 分片读（每个 agent 读 8-10 份、
返回结构化五字段 + 与文件名的 diff），但汇总与判定必须回到主对话。

### Step 3 — ticker → RIC 解析

`Company.ticker` 用 LSEG RIC（`NVDA.OQ`、`0700.HK`、`002747.SZ`），
文件名/首页给的常是 Bloomberg/broker 风格，而且**同一份稿里就有两套**：
文件名写 Bloomberg 的 `NVDA.US`、首页印路透短式 `NVDA.O`。两个都要
喂进候选梯（去重后按序试），不要只信一边。候选梯：

| 输入后缀 | RIC 候选（按序） |
|---|---|
| US | N, OQ, A, K |
| O（路透短式，首页常见） | OQ, O |
| N / A / K（已是路透式） | 原样，失败再试 OQ |
| UN | N |
| UW / UQ | OQ |
| UR | A |
| JP / JT | T |
| SW | S |
| GR / GY | DE |
| FP | PA |
| LN | L |
| IM | MI |
| NA | AS |
| AU | AX |
| TT | TW |
| CN | TO |
| HK | root 补零到 4 位 + `.HK`（`700.HK → 0700.HK`） |
| 裸 6 位数字 | `60/68/90` 开头 → 先 `.SS` 后 `.SZ`；否则先 `.SZ` 后 `.SS` |
| 其它/已是 RIC | 原样作为最后候选 |

每个候选逐一确认（**永不盲信**）：

```bash
curl -s -o /dev/null -w '%{http_code}' -H "Cookie: auth-token=$MT_TOKEN" \
  "$MT_BASE/api/v1/companies/<candidate>"
```

200 → 命中即停；全部 404 → 兜底搜一次
`GET /api/v1/companies?q=<root>&limit=20`，仅当**恰好一个**结果的
ticker root 完全相同才接受；0 个或多个 → 「待人工」。

### Step 4 — 晚传预判

```bash
curl -s -H "Cookie: auth-token=$MT_TOKEN" "$MT_BASE/api/v1/admin/source-lag-rules"
```

按**归一化键**（NBSP→空格、折叠空白、strip、lower）匹配该行来源：
- 规则 `lag_days = null` → 永久豁免，永不晚传
- 规则 `lag_days = N` → `today - publish_date >= N` 即晚传
- 无规则 → 默认 30 天口径判断，行上另标「来源未配置规则」

规则表没命中时，再查一次**存量目录用的写法**（prod 也能用，不需要
数据库）：

```bash
curl -s -H "Cookie: auth-token=$MT_TOKEN" \
  "$MT_BASE/api/v1/analysts/search?q=<broker关键词>&limit=10"
```

返回 `{name, source}`，`source` 就是目录里在用的规范拼写。Step 2 的
source 裁决拿它当第二依据：首页印 `Citi Research`、这里回 `Citi` →
用 `Citi`。两处都查不到 = 真新来源，标出来让用户确认拼写再传。

晚传行不算失败，单独成节等确认（见 Step 5）。

### Step 5 — 汇总表 + 确认闸（不可跳过）

输出 Markdown 表：

```
| # | 文件 | 标题 | 来源 | 公司(RIC) | 日期 | 分析师 | 校验 | 状态 |
```

「校验」列写 double-check 结论：`全一致` / `标题冲突(并排展示)` /
`✨内容补齐` 等。状态分四节列出：

1. **✓ 就绪** — n 行，确认后直接传
2. **⚠ 晚传** — 逐行列出 `发布日期已过 <来源> 的 N 天滞后期，上传后
   约一小时内会被清扫下架`；需要用户逐行或整节点头才带
   `confirm_late` 上传
3. **⚠ 字段冲突** — 首页 vs 文件名不一致的行，并排两个值，用户裁决用哪个
4. **✗ 待人工** — 公司解析不出/歧义、无 ticker（宏观稿）、读不出首页；
   给出原因，不上传

然后**停下来等用户答复**（用 AskUserQuestion 或直接问）。用户可以说
"就绪的都传，晚传的只传第 3 行，冲突的用首页标题"这类局部指令——
按指令执行，未提到的行不动。

### Step 6 — 上传

认证与地址（缺了先问/先取，token 只进变量）：

- local：`MT_BASE=http://localhost:<api_port>`；token 用 `just token`
  （在 web_new 仓库根目录，需 dev 栈已起）
- prod：`MT_BASE=https://api-production-5af8.up.railway.app`；token
  **让用户提供**（或 `op run` 注入）。PR #448 设想的 Keychain item
  `moneytalk-dt-uploader` 在本机**并不存在**（实测
  `security find-generic-password -s moneytalk-dt-uploader` exit 44）——
  先查 exit 0 才用，别假设它在。**prod 上传在 Step 5 已确认过一次，
  这里不再追问但也不扩权**——只传确认过的行。

逐行（并发无益，顺序即可）：

```bash
curl -s -w '\n%{http_code}' -H "Cookie: auth-token=$MT_TOKEN" \
  -F "ticker=<RIC>" -F "title=<标题>" -F "analyst=<分析师，无署名填—>" \
  -F "source=<来源>" -F "publish_date=<YYYY-MM-DD>" \
  -F "confirm_late=<true 仅限已确认晚传行>" \
  -F "file=@<pdf路径>;type=application/pdf" \
  "$MT_BASE/api/v1/admin/upload-pdf"
```

状态码 → 桶：

> **顺序陷阱（读过后端确认）**：服务端**先查晚传、后查公司**。所以一行
> 若既晚传又公司不存在，返回的是 409 而不是 404——**不能**把 409 读成
> "公司没问题，只是日期晚了"。带 `confirm_late` 重传后才会暴露 404。

| 响应 | 桶 | 说明 |
|---|---|---|
| 201 | `uploaded` | 新建成功 |
| 200 且响应 `retired_at` 为 null 且此前该 sha 对应退休行 | `restored` | 撞上已退休的同内容行，服务端已自动复活并重新入索引。**复活即固定**（`retire_pinned_at` 置位）——这行以后不会再被清扫下架 |
| 200 | `duplicate` | 已存在（sha256 命中），响应里有已存在的 report id |
| 404 | `unknown_company` | 理论上 Step 3 已拦；出现说明解析退化，回「待人工」 |
| 409 `late_upload_lag_elapsed` | 回 Step 5 | 只会发生在未带 confirm_late 的行——不得自作主张重试，回去要确认 |
| 409 `duplicate_pdf_under_different_ticker` | `conflict` | 同字节 PDF 已挂在**另一家**公司下，列出两边 id 让用户处理 |
| 400 `unsupported content-type` | `failed` | 客户端发了非 pdf 的 content-type。curl 会按 `.pdf` 扩展名自动推断，所以漏写 `;type=` 通常没事——但扩展名不是 `.pdf` 的文件会以 octet-stream 发出被拒；稳妥起见总是显式写 |
| 413 | `failed` | 超 50MB（`upload too large (max 52428800 bytes)`） |
| 422 | `failed` | 表单字段空串/**纯空白也算缺失**（FastAPI 直接 `Field required`），或 app 级 `source must not be blank` |
| 5xx | 重试 ≤3（间隔 5s），仍失败进 `failed` |

`analyst` **必须给非空白值**——空串和纯空格都会被表单层当缺失打回 422
（实测）；没有署名就填 `—`（与服务端对无效署名的归一值一致）。
`confirm_late` 每行都显式写 `true`/`false`，别留空。

上表每一行状态码都在本地栈实跑验证过
（201 / 200-dup / 200-restored / 404 / 两种 409 / 400 / 413 / 422 各≥一次）。

### Step 7 — 收尾汇总

分桶计数 + `conflict` / `failed` / 「待人工」逐行明细。失败行给出
单行可复制的重试命令。最后提醒：非豁免来源的**新建**（201）手动上传
会在滞后期满后被清扫自动下架（这是设计，不是事故）；`restored` 行
例外——复活时已被固定，不会再下架。

## 已知边界

- 无 ticker 的宏观/行业稿：现有端点必填公司，只能进「待人工」。
- 扫描版 PDF（首页无文字层）：Read 仍可视觉识别，但字段置信度降一档，
  一律并入「字段冲突」节让用户看一眼。
- 单文件 >50MB：端点会 413，先在表里标出。
