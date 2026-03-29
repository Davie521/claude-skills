# Claude Skills

A collection of Claude Code plugins for development workflow automation, writing assistance, and productivity tools.

## Plugins

### dev-workflow

Automated development workflows for Claude Code.

| Skill | Command | Description |
|-------|---------|-------------|
| **cpr** | `/cpr` | Git PR pipeline: detect status -> commit -> create PR -> wait for CI -> fix failures -> check Copilot comments -> loop until all green |
| **cl** | `/cl` | Copilot Lint review: check CI -> run local lint/build -> critically review Copilot comments -> fix only necessary issues |
| **impl** | `/impl` | Multi-agent implementation: Plan (2-3 rounds) -> Implementer (worktree) -> Reviewer -> Tester -> Reviewer -> PR |
| **browser** | auto | Browser MCP routing: auto-select browser-use, Chrome DevTools, or Playwright based on intent |

### writing

AI-assisted writing with a structured 4-phase workflow.

| Skill | Description |
|-------|-------------|
| **vibe-writing** | Socratic dialogue -> knowledge cards -> structure -> write -> finalize. Supports starting from scratch, existing ideas, or drafts. |

### document

Document creation tools.

| Skill | Description |
|-------|-------------|
| **cheatsheet** | Create dense, printable A4 landscape cheatsheets (5-column, 6pt font) from Markdown. Supports math, tables, highlights, multi-page output. |

### work-tools

Work integrations (Feishu/Lark messaging and document operations).

| Skill | Description |
|-------|-------------|
| **feishu** | Feishu (Lark) MCP integration: send messages, create groups, create documents, upload files |

## Installation

Install individual plugins via Claude Code CLI:

```bash
# Install all plugins from this marketplace
claude plugins add Davie521/claude-skills dev-workflow
claude plugins add Davie521/claude-skills writing
claude plugins add Davie521/claude-skills document
claude plugins add Davie521/claude-skills work-tools
```

## Usage

After installation, simply type the command in Claude Code:

```
> /cpr          # Push code through full PR pipeline
> /cl           # Review and fix Copilot lint comments
> /impl         # Multi-agent coordinated implementation
> write an article about...   # Triggers vibe-writing
> create a cheatsheet for...  # Triggers cheatsheet
```

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- GitHub CLI (`gh`) for cpr/cl workflows
- Browser MCP servers for browser skill (see skill docs for setup)
- Feishu MCP server for feishu skill

## License

MIT
