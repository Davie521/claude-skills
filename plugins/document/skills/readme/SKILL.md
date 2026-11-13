---
name: readme
description: "Write, rewrite or audit a repository README in Yifan's style: the first screen says what it does and shows the real thing, one-step install, honest limits, details moved to docs/, every command and number checked against the code, no AI tone. Covers public projects (English + README.zh-CN.md) and private tools whose readers are future-you and an agent. Use when the user says 'README', '写 README', '改 README', '整理文档首页', 'README 太长/太像 AI 写的', '开源前收拾一下仓库', or a new repo needs its front page."
---

# readme — 写 README

README 是仓库的门口，不是仓库的全部文档。它只回答读者刚到时的几个问题：**这是什么、跟别的有什么不同、怎么装上、有什么限制、细节去哪看**。其余都搬进 `docs/`——「它们有价值，只是不该挡在门口」。

范本：作者自己的 `Davie521/ai-ghostty-notifier` 和 `Davie521/xiayule`，拆解见 [references/exemplars.md](references/exemplars.md)。动笔前至少读一遍。外部参考和取舍见 [references/sources.md](references/sources.md)。

## 三种模式

- **新写**：走下面 0–5 全部。
- **改写 / 更新**：先审再改。先 `git status`（别把别人改到一半的东西卷进来），再 grep 测试和 CI 里有没有钉住 README 文字的断言。保留作者原有的语气、徽章、装饰，除非用户同意删；作者亲手写的 README 不许整篇静默覆盖。内容是「搬走」不是「删掉」——搬去 `docs/` 并留链接。带过来的每个事实都要重新核实。
- **审查（用户说「看看 README 有什么问题」）**：只出报告，不动文件。按 [references/checklist.md](references/checklist.md) 逐项给结论，最后列「一个陌生人读到哪里会放弃」。命令跑不了（要 docker、OAuth 凭据、付费 token）时，从代码推出**照着 README 走会在哪一步失败、报什么错**，写成「README:行 ↔ 代码文件:行」，并标明是实测还是读代码推断——这往往是最有价值的发现。

## 0. 先定读者和体裁

| 体裁 | 读者 | 骨架 |
|---|---|---|
| **公开工具 / App** | 路过 GitHub 的陌生人，30 秒决定留不留 | 下面「公开项目骨架」 |
| **有在线 Demo 的 Web App** | 想先试试的人，少数人才自托管 | 同上，但第 5 步画面旁边放 Demo 链接，第 9 步拆成「试用」（Demo、测试账号）在前、「自托管」在后；自托管要写清必填环境变量、外部服务（OAuth、第三方 API）、部署限制（单实例、不能 Serverless 之类） |
| **库 / SDK** | 要调用它的开发者 | 同上，但「看到什么」换成最小可运行代码 + 输出 |
| **私人工具仓库** | 将来的自己、接手的 agent | [references/exemplars.md](references/exemplars.md) 末节「私人工具仓库」 |
| **课程作业 / 研究** | 老师、面试官 | 一句话做了什么 + 结果数字/图 + 怎么复现 + 目录 |

拿不准就问一句「这个 README 给谁看」，别两头兼顾写成大杂烩。

## 1. 先收事实，再动笔

README 里每个命令、路径、数字、默认值、依赖版本都必须有出处。先读代码，把事实列成清单（每条带 `文件:行`）：

- 入口和安装：`install.sh` / `setup.sh` / `Makefile` / `package.json` scripts / release 产物——**实际**装到哪、改了用户什么设置、不碰什么
- 配置项：变量名、默认值、在哪改
- 行为里的具体数字：阈值、间隔、上限、超时
- 依赖与最低版本：CI 矩阵里真跑过的版本才算数
- 限制和降级：免费版缺什么、哪些平台不支持、出错时怎么表现
- 卸载：装的时候改过的每一处，包括全局偏好、launchd、钩子
- 已有的 `docs/`、`CHANGELOG`、`LICENSE`、`.github/workflows/*`

**核实不了的说法不写进 README**：要么删，要么在交付时单独告诉用户「这几条我没法核实」。编出来的参数、路径比没有示例更糟。

改已有 README 时，先跑「反向审计」：文档提到的文件/命令/选项是否都还存在；仓库里重要的受控文件（CI、安装脚本、配置样例）是否有文档提到。

## 2. 公开项目骨架

按顺序，每节能删就删：

1. **标题** —— 项目名。有真 logo 就居中放，没有就别凑。
2. **一句话** —— 只说效果，最好带一个对照：「不告诉你『今天有雨』，告诉你几点下、几点停。」/「Long runs tell you the moment they finish. Short ones never interrupt you.」不写「a powerful / lightweight / modern tool for…」。GitHub 仓库的 About 描述要和它说同一件事（不必逐字一致，不能一个说 A 一个说 B）；对不上就建议一句新的，改 About 用 `gh repo edit --description`，先问。项目已停更、是非官方的、或协议不允许商用，就在这附近说，别藏到最后。
3. **徽章（可选，≤4 个）** —— 只放会变且有信息量的：CI、最新版本、License、平台。
4. **语言切换** —— 有中英两版时：`English · 中文`。
5. **真实画面** —— 实机截图、真实通知、录屏动图；**不放 mockup、不放 AI 生成图**。先在仓库里找（`docs/`、`screenshots/`、`assets/`、release 附件），常有截好了没用上的；真没有再让用户截，或用 `run` skill 跑起来截。`alt` 写成一句完整描述，图挂了也能看懂。
6. **一段场景** —— 两三句，从用户的处境写起：「You start a long task, switch to the browser, and forget about it.」/「没雨的时候它只是个温度。」落在读者的决定或省下的事上。
7. **它是什么样 / Features** —— 二选一：
   - 能直接列出真实输出就列（菜单栏上显示的那几个字符串、命令的真实输出）；
   - 否则 Features：每条 `**粗体短判断。**` + 一两句带具体数字的说明，结论用动词短句不用名词（「Only when it is worth it.」而不是「Smart thresholds」），细节链到 docs。5–8 条。「不做什么」也可以是一条（No telemetry, no network）。
8. **Why not X（有明显替代品时）** —— 先承认替代品已经做到什么，再一张对比表列差异，行是读者关心的维度。最后说两者共存会怎样。
9. **安装** ——
   - 一条命令优先（release 产物 > clone + 脚本 > 手动步骤）。
   - 紧接着说它**改了什么、装到哪、为什么这么装、代价**。
   - 只写读者**还剩下要自己做的事**（授权、填 token、改默认坐标、重启会话），按真实状态写，别写已经自动完成的。
   - 预判第一次试用的困惑（「试一下看不到任何东西，因为不到 3 分钟不提醒」），给验证方法。
   - 可选：给一段「交给 agent 装」的提示词，配一份写给 agent 的 `docs/agent-install.md`（规则、前置检查、每步验证、只能人做的步骤）。
   - 升级坑单独一段，以 `**Upgrading from X:**` 开头。
   - Requirements 一行，说清哪个依赖只在什么情况下需要。
10. **限制** —— 能做成一节标题就做成标题（「免费版拿不到分钟级」）。说缺什么、怎么降级、界面上怎么标、够不够用。
11. **Docs 一行** —— `Configuration · How it works · Troubleshooting · Uninstall · Changelog`，链到 `docs/` 的锚点。
12. **卸载（装的时候改过全局状态就必须写）** —— 每一步 + 为什么不能省 + 卸完会看到什么。
13. **Credits / License** —— License 用白话说能做什么、不能做什么；非标准协议（Commons Clause、CC BY-NC）尤其要说。

**搬去 docs/ 的**：完整配置表、行为细则、原理、排障、调试命令、设计取舍、FAQ、版本历史。README 超过约 150 行（不算代码块）就该搬了。

**给维护者看的不放 README**：发版流程、架构图、目录树、开发环境细节进 `CONTRIBUTING.md` 或 `docs/`（作者的做法是 `docs/releasing.md`、`docs/reference.md`）。读者还不知道这是什么之前，别让他看到目录树。`CLAUDE.md` / `AGENTS.md` 是写给 agent 的，不当「架构文档」从 README 推给人；例外是专门写给 agent 照做的文档（如 `docs/agent-install.md`），可以从安装一节链过去。根目录散落的过程文件（`task_plan.md`、`progress.md`、`findings.md` 之类）建议用户挪走或忽略，别让访客第一眼看到。

**一个事实只住一处**：同一个阈值、命令、路径在 README 里只出现一次，其他地方链过去。重复的那份迟早会过时。

## 3. 文风

照作者自己的提交原话：「每节一张表、满屏加粗、面面俱到的 FAQ、『三道防线』式排比——读起来像生成的，不像人写的。」

- 句子短，主语清楚，一句一个事实。数字代替形容词：「3–10 分钟静音提醒」而不是「智能提醒」。
- 粗体每节最多一两处，只给读者会踩的坑或真正的结论。
- 表格只在两个以上维度对比时用；单列信息用列表或段落。
- 不用：emoji 小标题、「🚀 Quick Start」、`✨ Features`、「强大 / 轻量 / 优雅 / 无缝 / 一站式 / 赋能 / blazing fast / seamless / robust / leverage」、三连排比、「总而言之」、空泛的 Roadmap、没人问过的 FAQ。
- 诚实：不写没实现的功能；非官方要写 disclaimer；依赖未公开接口要写会变；免费版的降级要说。
- 中文版不是逐句翻译：用中文的说法重写（「装」「卸载」「别的」都可以当小标题），但事实、命令、数字和英文版一致。
- 安装说明面向可能不熟的人，但不解释 `git clone` 是什么。

逐条对照 [references/checklist.md](references/checklist.md) 里的 AI 腔清单。

## 4. 核验（交付前必做）

1. **命令真跑**：在临时目录（`/tmp/readme-check-*`）按 README 从零走一遍安装和第一次使用；跑不了的（要付费 token、要签名）明确标「未实测」告诉用户，别默认它对。
2. **数字、默认值、路径**逐个回到代码对一遍。
3. **链接和锚点**：相对链接的文件存在；锚点用 `gh api /markdown` 渲染后核对（做法见 `gh-pr-traps` skill）。
4. **图片**存在、尺寸合适、不含隐私（真实手机号、邮箱、token、家庭住址、局域网 IP）。
5. 双语版本：两份的小节、命令、数字逐项对齐。
6. 过一遍 [references/checklist.md](references/checklist.md)。
7. **当一回陌生人**：假装第一次来这个仓库，从头读，记下在哪一行会想关掉页面、哪一步会卡住，改掉再交。

## 5. 交付

- 用一份「决定清单」汇报，不贴全文：删了什么、搬去哪、改了哪些不准的说法、哪些没法核实、哪些没实测。
- 提交信息写读者看到的变化，一句话说清：`docs: say what this does in the first screen` / `README 瘦身：229 行 → 60 行，细节移到 docs/notes.md`；正文写为什么改、实测发现了什么。
- 推送、开 PR 按项目惯例（cpr 或直接推），推之前先问，除非用户已经说过。
