# 参考来源（2026-11 调研）

**第三版（11/14）起，范本改用用户 star 过的高星仓库**（见 examples.md）：Claude-Code-Game-Studios、process-compose、SoftwareCopyright-Skill、writing-dna-skill、ios-simulator-mcp、LinuxMirrors。用户说自己仓库（xiayule 等）的 README 是 AI 写的，不能当范本。根据这些仓库，取消了「README 超过 150 行就搬走」这条：没有文档站的高星仓库，README 本身就是文档，常常有两三百行以上。

**第二版（11/14）的结构改动**：第一版是一份规则清单，用户看了觉得不够好。第二版照 better-readme 的写法，先立「漏斗」和「契约」两条主线，每条规则都写出原因；照 readme-polish 补了「什么时候不用」一节和汇报格式；照 Anthropic skill-creator 的建议，少写硬性的「必须」，多讲为什么，并把范本改成好写法和差写法的对照。

**第四版（11/14）的写法学自高星 skill 本身**（不是它们的 README）：
- `lieflat-less-ai-tone`（writing-dna-skill 仓库）：白名单式规则，每条有触发标记和 ❌/✅；「不作为改写理由」表；信息守恒（不许新增、不许删限定词）；最终验收要求每处改动都对上一条编号规则。→ 本 skill 的 ai-tone.md、硬性边界、最终验收。
- `software-copyright-materials`（SoftwareCopyright-Skill）：「强制人工门禁」，写明哪几步必须停下来等用户，不许默认继续。→ 「必须停下来问用户的地方」。
- `nature-paper-xray`（nature-skills）：先写「默认立场」；在描述里说清它不是什么，并指向兄弟 skill；没读完要说停在哪。→ 默认立场、「哪些不归这个 skill」。
- `code-review`（Claude-Code-Game-Studios）：报告每节都给状态，包括 NOT ASSESSED。→ 审查报告模板里的「未核对」。

## 别人写的 README skill

- [tommy0103/better-readme-skill](https://github.com/tommy0103/better-readme-skill)：最好的一份，第二版的骨架照它的思路写。采纳了这些：先审后改；前 50 行别放内部实现；维护者内容和用户内容分开；一个事实只住一处；「搬走不删」；带过来的事实重新核实；以陌生人身份重读；用决定清单汇报。
- [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit)（crafting-effective-readmes）：按新写、补充、更新、审查分模式；「别默认套开源模板」。
- [divar-ir/ai-doc-gen](https://github.com/divar-ir/ai-doc-gen)：不编造功能；核实不了的报告给用户，不写进 README。
- [HangYu8123/HarnessFlow](https://github.com/HangYu8123/HarnessFlow)：「编出来的参数比没有示例更糟」；别用散文复述代码。
- [LennartHennigs/Button2](https://github.com/LennartHennigs/Button2)：audit 参数只出报告。
- readme-polish（archived 在 majiayu000/claude-skill-registry-data）：结构完整，有什么时候用、什么时候不用、先审后改、常见坑和每条的原因、输出。它主张居中头图、emoji 功能列表、折叠块，这些在用户 star 的高星仓库里也被当成噪音（见 examples.md 第 11 节），**没采纳**；只借了结构，以及「把路线图写成已经上线的行为」这类坑。
- [thatrebeccarae/claude-marketing](https://github.com/thatrebeccarae/claude-marketing)：隐私清洗清单（内网 IP、Tailscale 地址、ssh 别名）。它默认加一排徽章，**没采纳**。

## 写给人看的指南

- Art of README（noffle）：认知漏斗；「在不更短的前提下尽量短」；限制放前面；关键信息别只放在图里；每个徽章都要问对读者有什么用。
- [standard-readme](https://github.com/RichardLitt/standard-readme/blob/main/spec.md)：短描述不超过 120 字符，和包管理器、GitHub 上的描述一致；正文超过 100 行加目录。
- [makeareadme.com](https://www.makeareadme.com/)：项目停更了要在开头说。它主张「宁长勿短」。第三版部分采纳了：没有文档站时，README 可以长，但要用问题当小标题、加目录。
- [GitHub Docs: About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)：只写上手所需的；用相对链接。
- [Diátaxis](https://diataxis.fr/)：教程、操作指南、参考、原理分开写，README 只负责指路。
- [passo.uno: What's wrong with AI-generated docs](https://passo.uno/whats-wrong-ai-generated-docs/)：AI 文档的毛病是语气泛泛、没写限制、看着写完了其实没人审过。
