# 范本：作者自己写得最好的两份 README

两份都是公开仓库，可以直接去读原文对照：

- `Davie521/ai-ghostty-notifier`（英文 + `README.zh-CN.md`，工具/App 类）
- `Davie521/xiayule`（中文，菜单栏插件类）

下面摘的是**它们为什么好**，以及从提交历史里看得出的改法。提交信息是作者自己（和审查）一轮轮改出来的，比任何外部指南都更接近作者口味。

---

## ai-ghostty-notifier

### 第一屏（从上到下）

1. 居中 logo（真设计过的图，144px）
2. 居中 `<h1>` 项目名
3. 居中粗体一句话，**只说效果**：
   > Long Claude Code and Codex CLI runs in Ghostty tell you the moment they finish. Short ones never interrupt you. One click brings back the tab.
   三个短句：什么时候提醒、什么时候不打扰、点一下回到哪。没有「a powerful tool for…」。
4. 4 个徽章：CI、最新 release、License、平台（`macOS 13+`）。都是**会变、能点、有信息量**的，没有 「made with ❤️」。
5. 语言切换 `English · 中文`
6. **真实 demo 动画**（作者本人录的，带双语字幕），`alt` 把整段视频讲了一遍——读屏用户和图挂了的人也看得懂。
7. 一行「▶ Watch it with sound (1 min)」外链

然后一段**场景**，不是功能：
> You start a long task, switch to the browser, and forget about it. When it ends, a notification tells you which session finished and how long it took…

### Features 的写法

每条 = **粗体短判断** + 一两句带具体数字的说明：

> - **Only when it is worth it.** Under 3 minutes: nothing. 3–10 minutes: a silent notification. 10 minutes or more: with sound. The thresholds are [configurable](…).

要点：粗体是结论不是名词（「Only when it is worth it」而不是「Smart thresholds」）；说明里是阈值、时长、具体行为；细节链到 reference。最后一条「**Nothing extra.** No Node, no telemetry, no network…」把「不做什么」也当卖点。

### 「Why not the built-in notifications?」

先**承认**内置功能已经能做什么（「Claude Code already notifies in Ghostty, and clicking that notification brings back its tab」），再用一张对比表列差异，表格行是读者关心的维度（When / Sound / What it says / Goes away）。最后讲两者共存时会怎样、怎么关掉重复的那个。诚实比贬低竞品更有说服力。

### Install

- **一条命令**装 release（签名、公证、不用 clone、不用工具链），并说清它会改什么、不碰什么（「without touching anything else in their settings」）。
- **或者交给 agent**：给一段可直接粘贴的提示词，agent 去照 `docs/agent-install.md` 做。那份文件开头写明「This file is written for a coding agent」，有 Rules（Merge, never rewrite / Stop at the first failed check）、前置检查命令、每步的验证。
- 写清**哪些步骤只能你自己做**（授权通知权限、重启已开的会话）。
- 预判第一次试用的困惑：「A quick prompt to try it shows nothing, because tasks under 3 minutes never notify」，然后告诉你怎么发一条测试通知。
- 升级的坑单独一段粗体开头（「**Upgrading from 0.9.x or earlier:**」），给原因 + 一条命令 + 「新装不受影响」。
- Requirements 一行收尾，并说清哪个依赖只在什么情况下需要。

### 剩下的

- **Docs 一行**：`Manual install · Behavior in detail · Configuration · How it works · Troubleshooting · Uninstall · Changelog · Contributing`，全部链到 `docs/reference.md` 的锚点。README 不展开。
- **Credits and license**：致谢启发来源；License 用白话说能做什么、不能做什么、商用找谁，以及历史版本仍是哪个协议。

### 提交历史里的改法（docs 相关）

- `docs: say what this does in the first screen, and move install contract into Install`
- `docs: install by handing an instruction to an agent; README keeps the effect`
- `docs: README shaped like its peers — features, one install step, docs links; behavior table moves to the reference`
- `docs: a real notification under the tagline, the one thing the README's peers all show`
- `install: say only what is left to do, and how to uninstall a release` —— 正文写的是**第一次真实安装时输出哪里不对**：叫一个没 clone 的人跑 `scripts/…`、刚授权完又说「macOS 会问你两次」、文件没变却叫人去 trust。结论：只说读者还剩什么要做，按真实状态说。
- `docs: lead with what the built-in alerts don't do, a new demo, a changelog, issue forms and a security policy`
- `docs: a bell is not silence, the no-typing condition, the 10-minute boundary, bounded hooks (review)` —— 审查抓出来的措辞不精确，逐条改。

规律：**README 只保留效果、一步安装、去哪看细节**；行为表、配置项、原理全搬到 reference；每个说法都按真实运行结果校正。

---

## xiayule（下雨了么）

### 第一屏

```
# 下雨了么

macOS 菜单栏天气插件。不告诉你「今天有雨」，告诉你几点下、几点停。

[实机截图：菜单栏显示「17-19时雨」，夹在真实图标中间]

没雨的时候它只是个温度。雨快来了亮起雨伞和时段，正在下雨时告诉你还有多久停。抬眼一次就知道要不要带伞。
```

一句定位用「不…，…」对照把差异说透；图是**实机截图**（提交：`README 封面换成实机截图：天气项夹在真实图标中间`）；接着一段讲三种状态下看到什么，落在读者的决定上（要不要带伞）。

然后一段交代来源与依赖：数据来自哪、精度、跑在什么上、「纯 Python 标准库，没有任何依赖」。

### 「菜单栏长什么样」

不用形容词，直接列三种状态下菜单栏上**真实显示的字符串**（`☀️ 28°` / `☂ 18-22时雨` / `🌧 46分停`），再一段说点开有什么、下雪时不会说成雨。

### 「装」

- 三行命令。
- 紧接着说 `install.sh` **干了什么**（拷副本到哪、改了 SwiftBar 什么设置）、**为什么这么装**（仓库随便挪不会让菜单栏变空），以及**代价**（改代码要重跑一次）。
- 拿 token 的步骤写到「创建应用时类型选『天气』」这种细节。
- 默认值的坑直说：「默认坐标在上海青浦徐泾（作者家门口），装完第一件事就是改掉」。
- 配置用一张三列小表（变量 / 说明），只放必须改的。
- 用量策略用短句列表，全是具体数字（6 小时 / 2 小时 / 30 分钟、每台机器 365 天最多 5000 次）。

### 「免费版拿不到分钟级」

把限制做成一节标题。说清楚免费版缺什么、插件怎么降级、在界面上怎么标注（「不假装自己有分钟级数据」），再用一对具体例子说差多少、够不够用。

### 「别的」与「卸载」

- 出错时的行为（退避、拿上次数据顶班、标明是几分钟前的）、日志在哪。
- 测试：命令 + 多少项 + 是否打真实 API；CI 文件**写出路径**（提交 `README 点名 ci.yml`：反向审计发现 ci.yml 没被任何文档提到）；为什么下限测 3.9（macOS 自带的 python）。
- 其余细节一句话列出主题，链到 `docs/notes.md`。
- 卸载：步骤 + **为什么第二步不能省**（只删目录会留下一个静默的坏状态，并写出那个状态长什么样）+ 卸载后会弹什么框、该点哪个。步骤是实测过的。

### 提交历史里的改法

`README 瘦身：229 行 → 60 行，细节移到 docs/notes.md`，提交正文原话：

> 原来的 README 什么都想说：每节一张表、满屏加粗、面面俱到的 FAQ、「三道防线」式排比——读起来像生成的，不像人写的。
>
> 现在 README 只回答三个问题：这是什么、怎么装、免费版有什么限制。… 这些硬细节全部搬进 docs/notes.md，它们有价值，只是不该挡在门口。

这是本 skill 反 AI 腔清单的出处。

---

## 私人工具仓库（另一种 README）

作者的私有仓库（家里跑的自动化工具）也有 README，但读者不同：**将来的自己和接手的 AI**。共同点：

- 开头一句：这是什么、跑在哪台机器上、什么时候由什么合并而来。
- 「目录」表：`目录 | 是什么 | 老位置`，每行写清入口文件和先读哪份文档。
- 「为什么放在这里 / 为什么拆成两个」：只解释**不显然的决定**及其原因（权限、静默失败），这是最省将来排障时间的段落。
- 「第一次在这台机器上装」：可复制的命令块，注释写在行尾。
- 「私密的东西」：什么不进仓库、敏感值换成什么占位符、真实值在哪个本地文件、提交钩子拦什么。**README 本身绝不写真实号码、IP、密钥。**
- 「常见问题」表：`现象 | 原因 / 处理`，现象用人实际看到的样子描述。
- 「别做的事」：会造成不可逆后果的操作。
- 定时任务表：`Label | 程序 | 做什么`。
