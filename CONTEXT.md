# Claude Skills

Yifan's personal Claude Code plugin marketplace. This file is the domain glossary — terms used to discuss the skill ecosystem itself. Format follows [`grill-with-docs/CONTEXT-FORMAT.md`](plugins/dev-workflow/skills/grill-with-docs/CONTEXT-FORMAT.md).

## Language

### Skill structure

**Plugin**:
A top-level directory under `plugins/` containing `.claude-plugin/plugin.json` and one or more **Skills**. Each plugin is independently installable through the Claude Code marketplace.
_Avoid_: package, module, addon.

**Skill**:
A directory under `plugins/<plugin>/skills/<skill-name>/` containing a `SKILL.md` file and optionally **Bundled resources**. Each skill is one slash command or one auto-triggered behavior.
_Avoid_: command (the slash invocation is one of several entry points), tool.

**Frontmatter**:
The YAML block at the top of every `SKILL.md` declaring `name` (the slash command) and `description` (the agent-facing trigger text). The single field a model sees when deciding to activate the skill.

**Trigger description**:
The portion of `description` that uses "Use when..." or "TRIGGER when:" phrasing to gate auto-activation. Distinct from human-facing summary text — it is written for the model, not the reader.

**Bundled resource**:
A sibling file inside a skill directory that the skill references on demand. Examples: `LANGUAGE.md`, `CONTEXT-FORMAT.md`, `ADR-FORMAT.md`, `scripts/<name>.sh`, `references/<topic>.md`. Loaded only when the skill explicitly opens it — does not enter context by default.
_Avoid_: helper, attachment.

### Migration vs graft

**Migration**:
Creating a NEW skill file in this repo by copying or adapting an external skill (typically from `mattpocock/skills` or another marketplace). Always carries an **Origin link**.
_Avoid_: import, copy, port (use these only as verbs in conversation, not as the noun for the artifact).

**Graft**:
Modifying an EXISTING skill in this repo by inserting an external insight (a section, a rule, a checklist item) without replacing the host skill. The host skill's original authorship is preserved; the inserted content carries a **Provenance** footer specifying which sections originated externally.

The distinction matters because **Migration** produces a new file under a new path, while **Graft** edits a file someone else originally wrote. Confusing the two leads to either accidentally deleting original content or duplicating work.

**Origin link**:
A footer at the bottom of a Migrated skill citing source repository and license, e.g. _"Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) — `engineering/diagnose`. License: MIT."_

**Provenance footer**:
A footer at the bottom of a Grafted skill specifying which sections were inserted from external sources versus which are original to this collection.

### Conventions

**Active-prompt pattern**:
Convention this repo uses where consumer skills (those that read but do not produce a piece of infrastructure) **surface missing infrastructure to the user** instead of silently falling back. Currently applied to skills that reference `CONTEXT.md` and `docs/adr/`: if the file is missing, the skill suggests creating one but does not block. See [`memory/feedback_context_md_active_prompt.md`](https://github.com/Davie521/claude-skills) for the rationale.
_Avoid_: passive fallback, conditional reference.

**CONTEXT.md culture**:
The discipline of maintaining a domain glossary (this file is one). Produced and maintained by `grill-with-docs` (primary producer) and `improve-codebase-architecture` (semi-producer when naming new modules); consumed by `diagnose`, `to-prd`, `triage`, `tdd-workflow`'s grafted insights, and `improve-codebase-architecture` itself.

## Relationships

- A **Plugin** contains many **Skills**.
- A **Skill** has exactly one `SKILL.md`.
- A **Skill** may include zero or more **Bundled resources**.
- A **Migrated** skill carries one **Origin link** in its `SKILL.md` footer.
- A **Grafted** skill carries one **Provenance footer** in its `SKILL.md`.
- An **Active-prompt pattern** is implemented in any **Skill** that consumes a piece of infrastructure that may not exist (currently: `diagnose`, `to-prd`, `triage`, `improve-codebase-architecture`).

## Example dialogue

> **Dev**: "We should pull `tdd` from matt's repo. Want me to migrate it?"
>
> **Reviewer**: "It's a graft, not a migration — we already have `tdd-workflow` at `plugins/quality/skills/tdd-workflow/`. The matt insights (horizontal-slicing anti-pattern, never-refactor-while-RED) are inserted into the existing SKILL.md. The host file's coverage rules and RED-gate validation discipline are original; the inserted sections get a Provenance footer at the bottom."
>
> **Dev**: "OK. So if I look at `git log` for that file, the original author shows as Yifan, and the matt content is attributed in the footer rather than the commit author?"
>
> **Reviewer**: "Yes — exactly. Migration is a new file with an Origin link; graft is an edit with a Provenance footer."

## Flagged ambiguities

- **"Skill" vs "Command"** — slash commands (`/cpr`, `/triage`, `/grill-me`) are one **invocation surface** for skills. The skill is the directory + SKILL.md; the command is the trigger. Use **Skill** when discussing the artifact, **command** only when discussing how the user invokes it.
- **"Migration" vs "Graft"** — see above. Resolved: distinct verbs and distinct artifacts. A migration adds a new file; a graft edits an existing one.
- **"Plugin"** — distinct from a Claude Code MCP plugin (which is a server-side integration like `chrome-devtools`). In this repo, "plugin" means a marketplace plugin under `plugins/`. When discussing MCP, say "MCP server".
