# 参考来源（2026-11 调研）

这份 skill 以作者自己的仓库为准（见 examples.md）。下面的外部来源，只在和作者写法不冲突的地方采纳。

**第二版（11/14）的结构改动**：第一版是一份规则清单，用户看了觉得不够好。第二版照 better-readme 的写法，先立「漏斗」和「契约」两条主线，每条规则都写出原因；照 readme-polish 补了「什么时候不用」一节和汇报格式；照 Anthropic skill-creator 的建议，少写硬性的「必须」，多讲为什么，并把范本改成好写法和差写法的对照。

## 别人写的 README skill

- [tommy0103/better-readme-skill](https://github.com/tommy0103/better-readme-skill)：最好的一份，第二版的骨架照它的思路写。采纳了这些：先审后改；前 50 行别放内部实现；维护者内容和用户内容分开；一个事实只住一处；「搬走不删」；带过来的事实重新核实；以陌生人身份重读；用决定清单汇报。
- [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit)（crafting-effective-readmes）：按新写、补充、更新、审查分模式；「别默认套开源模板」。
- [divar-ir/ai-doc-gen](https://github.com/divar-ir/ai-doc-gen)：不编造功能；核实不了的报告给用户，不写进 README。
- [HangYu8123/HarnessFlow](https://github.com/HangYu8123/HarnessFlow)：「编出来的参数比没有示例更糟」；别用散文复述代码。
- [LennartHennigs/Button2](https://github.com/LennartHennigs/Button2)：audit 参数只出报告。
- readme-polish（archived 在 majiayu000/claude-skill-registry-data）：结构完整，有什么时候用、什么时候不用、先审后改、常见坑和每条的原因、输出。它主张居中头图、emoji 功能列表、折叠块，这些和作者的口味相反，**没采纳**；只借了结构，以及「把路线图写成已经上线的行为」这类坑。
- [thatrebeccarae/claude-marketing](https://github.com/thatrebeccarae/claude-marketing)：隐私清洗清单（内网 IP、Tailscale 地址、ssh 别名）。它默认加一排徽章，**没采纳**。

## 写给人看的指南

- Art of README（noffle）：认知漏斗；「在不更短的前提下尽量短」；限制放前面；关键信息别只放在图里；每个徽章都要问对读者有什么用。
- [standard-readme](https://github.com/RichardLitt/standard-readme/blob/main/spec.md)：短描述不超过 120 字符，和包管理器、GitHub 上的描述一致；正文超过 100 行加目录。
- [makeareadme.com](https://www.makeareadme.com/)：项目停更了要在开头说。它主张「宁长勿短」，**没采纳**，作者的做法是短 README 加上 `docs/`。
- [GitHub Docs: About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)：只写上手所需的；用相对链接。
- [Diátaxis](https://diataxis.fr/)：教程、操作指南、参考、原理分开写，README 只负责指路。
- [passo.uno: What's wrong with AI-generated docs](https://passo.uno/whats-wrong-ai-generated-docs/)：AI 文档的毛病是语气泛泛、没写限制、看着写完了其实没人审过。
