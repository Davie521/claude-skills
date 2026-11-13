# 好写法和差写法

这里的「好」都摘自作者自己的两个公开仓库，可以去读原文对照：`Davie521/ai-ghostty-notifier`（英文，另有中文版）和 `Davie521/xiayule`（中文）。「差」是同一件事常见的 AI 写法。每组后面一句说明为什么。

## 目录

1. 一句话
2. 第一屏的画面
3. 场景段
4. 功能
5. 和替代品比
6. 安装
7. 限制
8. 卸载
9. 私人仓库的开头
10. 作者自己改 README 时留下的话

---

## 1. 一句话

差：
> 下雨了么 is a powerful, lightweight macOS menu bar weather plugin built with Python and SwiftBar.

好：
> macOS 菜单栏天气插件。不告诉你「今天有雨」，告诉你几点下、几点停。

差的那句全是形容词和技术栈，读者看完还是不知道它跟系统自带的天气有什么不同。好的那句用一个对照，直接说出差别在哪。

差：
> A notification tool for Claude Code and Codex.

好：
> Long Claude Code and Codex CLI runs in Ghostty tell you the moment they finish. Short ones never interrupt you. One click brings back the tab.

三个短句各回答一个问题：什么时候会提醒、什么时候不打扰、点一下之后会怎样。

## 2. 第一屏的画面

差：用设计软件画一张示意图，或者 AI 生成一张「科技感」封面。

好：实机截图，天气那一项夹在菜单栏的真实图标中间；或者作者本人录的演示动画，配双语字幕。`alt` 把画面内容完整写一遍：

```html
<img src="docs/menubar.png" width="331" alt="菜单栏显示「17-19时雨」">
```

读者靠画面判断「这是真的在跑的东西」。夹在真实图标中间，还顺带说明了它在屏幕上有多大。

## 3. 场景段

差：
> ## ✨ Why ai-ghostty-notifier?
> In today's fast-paced AI development workflow, staying productive is crucial…

好：
> You start a long task, switch to the browser, and forget about it. When it ends, a notification tells you which session finished and how long it took, and **Go to tab** brings that session's tab forward.

好的那段从读者自己会遇到的处境写起，到他得到的结果为止，中间没有一个形容词。

## 4. 功能

差：
```
- 🧠 **Smart Thresholds** — Intelligent notification timing
- 🎯 **Precise Navigation** — Seamless tab switching
```

好：
```
- **Only when it is worth it.** Under 3 minutes: nothing. 3–10 minutes: a
  silent notification. 10 minutes or more: with sound. The thresholds are
  [configurable](docs/reference.md#configuration).
- **Nothing extra.** No Node, no telemetry, no network.
```

好的那组，粗体写的是结论，不是功能名；后面跟的是读者可以拿来和自己情况对比的数字，细节链到 docs。「不做什么」也能单独算一条。

另一种做法是不写功能列表，直接列出真实的输出：

```
- 没雨：`☀️ 28°`
- 三小时内有雨：`☂ 18-22时雨`
- 正在下雨：`🌧 46分停`
```

## 5. 和替代品比

差：不提替代品；或者一句「比 X 更好用」。

好：先承认替代品已经能做到什么，再用一张表比较读者关心的几个方面：

> Claude Code already notifies in Ghostty, and clicking that notification brings back its tab. What differs is when you hear about a run, and how often:

| | Built in | ai-ghostty-notifier |
|---|---|---|
| **When** | About a minute after every reply | The moment a run ends, only for runs of 3 minutes or more |
| **Sound** | Every time | None under 10 minutes |

表后面再说清两者同时开着会怎样，以及怎么关掉重复的那个。

## 6. 安装

差：
```
1. Clone the repo
2. Run `npm install`
3. Configure your settings
4. Enjoy! 🎉
```

好：一条命令，然后说清这条命令做了什么，再列出只有人能做的事：

> One command installs the current release: a signed, notarized build, no clone, no Swift toolchain. It installs the app, then registers the hooks for whichever of Claude Code and Codex CLI it finds, without touching anything else in their settings.
>
> …two things stay with you: allowing the notification and Automation permissions, and restarting the CLI sessions you already have open.
>
> A quick prompt to try it shows nothing, because tasks under 3 minutes never notify. The installer ends with a test notification instead…

装到哪、为什么这样装、代价是什么，也一并交代：

> `install.sh` 把脚本拷到 `~/Library/Application Support/xiayule/plugin/`……**跑起来的是那份副本，不是仓库里这份**——所以仓库随便挪、随便改名都不会让菜单栏变空。代价是改完代码要重跑一次 `./install.sh` 才生效。

要给读者留一段「交给 agent 装」的路径时，给一段可以直接粘贴的提示词，再配一份写给 agent 看的 `docs/agent-install.md`，里面写规则、前置检查、每一步怎么验证、哪些步骤只能人来做。

## 7. 限制

差：把限制放进文末的 FAQ，或者干脆不提。

好：把限制直接做成一节的标题：

> ## 免费版拿不到分钟级
>
> 彩云的分钟级降水和气象预警属于企业套餐的增值项，免费 token 没有。插件会降级到小时级，并在页脚灰字标一句「时段为小时级精度」——不假装自己有分钟级数据。

这一节说了缺什么、插件怎么降级、界面上怎么标出来，再举一对例子说明差多少、够不够用。

## 8. 卸载

差：
> To uninstall, delete the folder.

好：写出每一步，说明为什么不能省，并告诉读者卸完会看到什么：

> 第二步不能省。`install.sh` 改的是 SwiftBar 的**全局偏好**，只删目录的话它会一直指着一个不存在的路径——而那个状态是静默的……
>
> 删掉偏好之后 SwiftBar 再启动会弹一个 **Set SwiftBar Plugins Location**……真要卸载就选 `Quit SwiftBar`。

安装时改过全局状态的项目，卸载这一节最容易漏写，也最需要实测。

## 9. 私人仓库的开头

读者是将来的自己和接手的 agent，他们来的时候心里已经带着一件要做的事。所以开头先「按任务指路」，然后才是目录：

```markdown
## 要做什么，先读哪份

| 要做的事 | 先读 / 先跑 |
|---|---|
| 碰任何一台设备之前 | 先拿排队锁，见 `docs/排队规则.md` |
| 用某个风控严的平台 | 先跑 `quota take …`，放行了才动手 |
| 某功能突然不工作 | 跑 `xxx-refresh`，原因见 `docs/…/README.md` |
```

私人仓库最值钱的一节是「为什么这样放」。比如「仓库放在 `~/.local/share` 而不是桌面，是因为 launchd 读不了桌面，而且失败时是静默的」，这一句能省下将来半天的排障时间。

## 10. 作者自己改 README 时留下的话

下面是从提交记录里摘的，读者是谁、哪里写错了，原话说得最清楚：

- `docs: say what this does in the first screen`
- `docs: README shaped like its peers — features, one install step, docs links; behavior table moves to the reference`
- `docs: a real notification under the tagline, the one thing the README's peers all show`
- `install: say only what is left to do` —— 这次改动起因是第一次真实安装时，输出叫一个没有 clone 仓库的人去跑 `scripts/…`，还在用户刚授权完之后又说「macOS 会问你两次」。
- `README 瘦身：229 行 → 60 行，细节移到 docs/notes.md`，正文写的是：

  > 原来的 README 什么都想说：每节一张表、满屏加粗、面面俱到的 FAQ、「三道防线」式排比——读起来像生成的，不像人写的。现在 README 只回答三个问题：这是什么、怎么装、免费版有什么限制。
- `README 点名 ci.yml` —— 反向审计发现 CI 文件没有被任何文档提到。
