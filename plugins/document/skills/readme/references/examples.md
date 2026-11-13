# 范本：用户 star 过的高星仓库

下面每条都是从 GitHub 上真实的高星仓库里摘出来的。用户 star 了这些仓库，可以去读原文对照。每组后面一句话说明为什么值得学。

用户自己的仓库（xiayule、ai-ghostty-notifier 等）的 README 大多是 AI 写的，**不拿来当范本**。

| 仓库 | star | 类型 | 主要学它什么 |
|---|---|---|---|
| `Donchitos/Claude-Code-Game-Studios` | 3.9 万 | Claude Code 模板 | 开头就是第一条命令和接下来会发生的事；「已经证明了什么、还没证明什么」 |
| `F1bonacc1/process-compose` | 2.9 千 | Go 命令行工具 | 一句话、动图、两行「为什么」、最小可运行配置，然后才是功能 |
| `Fokkyp/SoftwareCopyright-Skill` | 6.3 千 | agent skill | 先说痛点，功能写得具体；把生成的样例放进仓库；环境要求附「预期输出」 |
| `larashero3-dotcom/writing-dna-skill` | 3.1 千 | agent skill | 用问题当小标题；「不是 X，而是 Y」；讲清楚为什么有效；写明边界 |
| `joshuayoes/ios-simulator-mcp` | 2.2 千 | MCP server | 安全公告放最上面；每个工具都写参数；「被谁提到过」用来证明可信 |
| `SuperManito/LinuxMirrors` | 7.8 千 | 脚本 | 第一屏就是适配系统版本的表 |

## 目录

1. 开头：用户第一件事做什么
2. 一句话和「为什么」
3. 先说痛点，再说做法
4. 功能写得具体
5. 给出真实产物
6. 已经证明了什么、还没证明什么
7. 讲清为什么有效
8. 安装：说清装哪个目录、怎么确认装对了
9. 边界
10. 小标题写成问题
11. 高星仓库里**不要学**的

---

## 1. 开头：用户第一件事做什么

**Claude-Code-Game-Studios** 标题下两句话就是承诺：

> Describe a game. Claude Code asks a few questions, writes a one-page brief, and builds a playable browser game from it. Then you change it, grow it and finish it, one step at a time.

第一个二级标题不是 Features，而是 **Make me a game**，先给出要打的第一条命令：

```
/prototype a fishing game where the rare fish only bite at dusk
```

接着用四步写清楚之后会发生什么，每一步都用粗体短语开头：**A few questions.** / **A one-page brief.** / **A first build.** / **Checked before you get it.** 第四步老实写着交接卡的最后一句是「Not yet played by a person」。

为什么好：读者一上来就知道这东西怎么用、会产出什么，不用先读一堆功能名再去猜。agent 类、模板类的仓库尤其应该这样开头。

## 2. 一句话和「为什么」

**process-compose** 的开头从上到下是这样的：

1. 一句话：`Process Compose is a simple and flexible scheduler and orchestrator to manage non-containerized applications.`
2. 一张演示动图
3. 两行「为什么」：`**Why?** Because sometimes you just don't want to deal with docker files, volume definitions, networks and docker registries.`
4. 一份最小的 `process-compose.yaml`，加一句「And start it by running `process-compose`」
5. 然后才是功能列表和 TUI 截图，安装和完整文档都链到官网

为什么好：「为什么」这句是站在读者的处境说的，说的是不想碰 docker 那堆东西，而不是在说自己有多强。最小例子能直接复制去跑。整份 README 只有 107 行，因为另有一个文档站。

## 3. 先说痛点，再说做法

**writing-dna-skill**：

> 很多人让 AI 模仿一个作者，通常只会给几篇例文，然后说「照这个风格写」。这种方式很容易失真，因为 agent 只是在凭感觉抓表面语气。
>
> `writing-dna-skill` 的思路是：不要让 agent 直接模仿，而是先让它系统分析一批完整文章，把风格拆成可复用的规则……

**SoftwareCopyright-Skill**：

> 软件著作权申请本身不神秘，真正麻烦的是整理材料：申请表字段要写对，操作手册要像样，代码材料要按规则截取……很多开发者最后会把这件事交给付费代办……

为什么好：先说出读者正在用、但不好用的那个办法，再说这个项目换了什么思路。读者会在第一段认出自己的处境。

## 4. 功能写得具体

**SoftwareCopyright-Skill** 的功能列表：

> - **从真实源码抽取代码**：代码材料只来自开发者已有项目，禁止 AI 编造源码，适合对材料真实性敏感的开发者。
> - **自动处理前 30 页 / 后 30 页规则**：源码足够时按常见鉴别材料要求生成前 30 页和后 30 页；不足 60 页时按规则生成全部代码材料。
> - **关键节点都让你确认**：业务口径、申请表字段、代码选择、截图方式、最终 Markdown 草稿都会停下来让开发者确认……

每条都是「粗体短句 + 具体做法 + 适合谁或解决什么」。像「30 页」「`申请表信息.txt`」这样的数字和文件名，读者可以拿去核对。

对比 **process-compose** 的功能列表：每条只有一行短语，没有加粗，但都是具体能力（`Health checks (liveness and readiness)`、`Run Multiple Replicas of a Process`）。项目的能力本身就很具体时，短语就够了。

差写法：`- 🧠 **Smart Design** — Intelligent, seamless experience`。没有一个读者能核对的信息。

## 5. 给出真实产物

- **SoftwareCopyright-Skill** 把一整套生成结果放进仓库的 `生成demo/软件著作权申请资料/`，并在功能列表里链过去：「可以直接点击查看生成后的草稿、正式资料和填报辅助文件」。另外有一张 6 格的演示截图表。
- **process-compose** 放了演示动图和 TUI 截图。
- **ios-simulator-mcp** 在第一屏放了一段演示视频。

为什么好：产出物是什么样，比任何描述都有说服力。产出是文件的（文档、配置、报告），就把样例提交进仓库；产出是界面的，就放截图或录屏。截图必须是现在的界面。

## 6. 已经证明了什么、还没证明什么

**Claude-Code-Game-Studios** 的 **What it has been shown to do**：

> - **The first build.** In a blind comparison on three game ideas, the brief made from its questions was picked over a hand-written brief all three times. …so on the games themselves the two kinds of brief tied.
> - **Growing.** One game was grown from its first build through six stories into a game the tester would keep building. That is one game, not yet a pattern.
> - **Not yet shown:** the engine route (Godot, Unity, Unreal)… Both are built and pass the framework's own checks, but neither has had a test like the two above.

为什么好：有证据的写证据，样本小的直接说样本小，还没测的写成「Not yet shown」。这比一句「powerful」可信得多。连「打平」这种不利的结果也照实写了。

## 7. 讲清为什么有效

**writing-dna-skill** 用一张表，把风格拆成 L1 到 L6 六层：每层分析什么、产出哪个文件。后面还有一节 **为什么有效**，以及「使用蒸馏好的风格」里的规则优先级：

> 规则冲突时的优先级：用户本次的明确指令 > 匹配当前体裁的结构模板 > 语言特征与视觉风格 > 认知框架。

为什么好：方法类、agent 类项目，读者最怀疑的是「这不就是一段提示词吗」。把机制拆开讲，并且说清冲突时听谁的，读者才会信。

## 8. 安装：说清装哪个目录、怎么确认装对了

**SoftwareCopyright-Skill**：

> 真正的 Skill 位于：`software-copyright-materials/`。安装时不要把仓库根目录当作普通单个 skill 复制。

环境要求逐项写明版本，并附上怎么确认：

```bash
officecli --version
# 预期输出：1.0.151
```

还写了为什么要锁版本：「避免同一份材料因工具版本漂移产生不同结果」。可选依赖单独列出来，写明只在什么情况下才需要。不会用 Git 的用户也给了一条路：「`Code` -> `Download ZIP`」。

**writing-dna-skill** 的「快速上手」只有四步，还附一句可以直接复制的开场白：

```text
请使用 writing-dna-skill 蒸馏分析这个目录里的所有文章。
```

为什么好：agent skill 最常见的安装错误，就是复制错了目录、装错了版本。所以要明确说装哪个目录，并给出「预期输出」，让读者自己确认装对了。

## 9. 边界

- **writing-dna-skill** 有一节 **重要边界**：只用于学习和风格研究，不要冒充作者本人；公开仓库不应包含未经授权的原文语料。
- **SoftwareCopyright-Skill** 在功能概览的第一行加了引用块：**本项目完全免费。请不要相信任何使用本项目包装出来的付费服务。**
- **ios-simulator-mcp** 把安全公告放在最上面：`Command injection vulnerabilities present in versions < 1.3.3 have been fixed. Please update to v1.3.3 or later.`

为什么好：读者最需要知道的风险和限制，放在他一定会看到的位置。

## 10. 小标题写成问题

writing-dna-skill 的小标题依次是：它解决什么问题 / 适合什么 / 它能分析什么 / 蒸馏流程 / 快速上手 / 为什么有效 / 重要边界。

为什么好：读者心里本来就带着这些问题。小标题直接对应问题，读者扫一眼就能跳到想看的那节。README 长了（200 行以上）也不至于迷路，再配一个目录就更好找。

## 11. 高星仓库里不要学的

高星不等于每个写法都好。下面这些在用户 star 的仓库里也出现过，但不要照搬：

- **营销横幅**：open-design 在第一屏放了充值优惠「Go credits are doubled」，这是商业推广，不是信息。
- **一排没有信息量的徽章**：process-compose 的 `Made with Go`、`Maintained? yes`、`PRs Welcome`。CI、版本、协议这类会变的徽章才有用。
- **赞助、其他项目、「New Skill」推荐挡在介绍前面**：ui-ux-pro-max-skill 在一句话介绍和正文之间，插了赞助链接和其他项目的推荐。
- **把发起人的商务信息放在最前**：nature-skills 的第一节是「项目发起人与运营信息」，包括代充、商务合作。读者要往下翻好几屏才看到「快速开始」。
- **版本更新日志占据开头**：ui-ux-pro-max-skill 的第一个二级标题是「What's New in v2.0」，没用过 v1 的读者读起来没有上下文。
