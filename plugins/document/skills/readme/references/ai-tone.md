# README 里的 AI 腔：改哪些、不改哪些

这一份是白名单：只改下面列出来的写法，每条都有能在原文里指出来的触发标记。没命中的句子不动，不能凭「读起来像 AI」的感觉改。中文 README 的句子层面（翻案腔、顿号罗列、破折号、冒号等）装了 `lieflat-less-ai-tone`（writing-dna-skill 仓库里自带）就用它处理，它的规则有实测数据；本文件只管 README 特有的写法。

## 不作为修改理由

下面这些看着像 AI 写的，但在用户 star 的高星仓库里人写的也很常见，不能拿它们当修改理由。

| 特征 | 为什么不改 |
|---|---|
| 小标题写成问题（「它解决什么问题」） | writing-dna-skill、ios-simulator-mcp 都这样写，读者扫一眼就能找到要看的那节 |
| README 很长 | 没有文档站时，README 本身就是文档，高星 skill 仓库常有 200–700 行 |
| 功能列表每条都用粗体开头 | SoftwareCopyright-Skill、Claude-Code-Game-Studios 都这样写；问题在于粗体后面有没有具体内容，不在于用没用粗体 |
| 配置、环境变量、兼容版本用表格 | 这是有多个维度的信息，表格最合适（LinuxMirrors 第一屏就是一张适配表） |
| 有徽章 | 作者喜欢的就保留；只处理第 6 条说的那种 |
| 居中标题和 logo | Claude-Code-Game-Studios、open-design 都这样做；只要不把介绍挤下去就行 |
| 正文里的「首先……然后」 | 讲步骤时这是正常写法 |

## 改写规则

### AI-1 空形容词

触发：一句话里，「强大 / 轻量 / 优雅 / 无缝 / 一站式 / 开箱即用 / 极致 / 智能」或 powerful、seamless、robust、blazing fast、cutting-edge、effortless、intelligent 后面，没有跟一个读者能核对的事实。

改法：换成那个事实。找不到事实就删掉这个形容词。

> ❌ A powerful, lightweight scheduler for your processes.
>
> ✅ A single binary with no other dependencies that schedules processes from one YAML file.

不改：形容词后面紧跟着具体证据的（「快：冷启动 40 ms，见 benchmarks/」）。

### AI-2 emoji 小标题

触发：二级、三级标题以 emoji 开头（🚀 Quick Start、✨ Features、📦 Installation）。

改法：删掉 emoji。作者明确想保留的就留着。

不改：正文里有含义的符号（✅/❌ 对照、⚠️ 警告），以及作者的品牌元素。

### AI-3 功能名代替功能

触发：功能列表里，粗体是一个名词短语（Smart Thresholds、Intelligent Engine），后面的说明也没有具体做法、数字或文件名。

改法：粗体改成结论，后面补具体做法。

> ❌ - **Smart Notifications** — Intelligent alerts that keep you in the loop
>
> ✅ - **Only long runs notify.** Under 3 minutes nothing happens; 10 minutes or more plays a sound.

不改：能力本身就具体的短语，比如 `Health checks (liveness and readiness)`。

### AI-4 推销式开头

触发：一句话介绍之前或紧跟着，出现「In today's fast-paced…」「在 AI 时代……」「Introducing…」「Meet X」「Say goodbye to…」这类开场白。

改法：删掉，直接从「它做什么」开始。

### AI-5 编造的场景和数字

触发：README 里的效果数字（「节省 80% 时间」「10x faster」）、用户评价、「被 N 家公司使用」，在仓库里找不到出处，比如 benchmark、测试记录、链接。

改法：删掉；或者换成有出处的，比如 Claude-Code-Game-Studios 那样写清楚「在三个游戏点子上做了盲测」。不改写成「可能节省很多时间」，这只是把编造变得模糊。

### AI-6 没有信息量的徽章

触发：`Made with X`、`PRs Welcome`、`Maintained? yes`、`Awesome`、`made with ❤️`，或者一排超过 6 个徽章。

改法：作者同意的话删掉。CI、最新版本、协议、平台这几类会变的徽章保留。

### AI-7 空占位小节

触发：Roadmap、FAQ、Support、Authors、Acknowledgments 这类小节，正文只有一两句套话（「Coming soon」「Feel free to open an issue」），或者 FAQ 里的问题没人真问过。

改法：删掉这一节。真有内容的就留下。

### AI-8 把限定说法改成断言

触发：改写时，原文或代码里的限定条件（「仅 macOS」「免费版没有」「实验性」「可能」）在新版本里没了，或者语气被加重了。

改法：恢复原来的限定。这条在改写已有 README 时最容易犯，因为限定说法看起来「不够干脆」。

### AI-9 用散文复述代码

触发：成段文字解释某个函数、某个类内部怎么实现，而这些内容读者在源码注释里就能看到。

改法：删掉这段，改成链接到对应文件（`src/lib/fair-allocation.ts` 的头部注释）。

### AI-10 来源不明的排比口号

触发：三个并列短句组成的口号（「更快、更稳、更省心」「三道防线」），或者每段结尾都是一句总结式金句。

改法：留下有具体内容的那一项，或者全部改成具体事实。
