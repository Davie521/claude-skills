---
description: Codex design challenge via MCP — asks "is this approach right?" not "are there bugs?". Surfaces assumptions, failure modes, alternatives. Read-only.
argument-hint: '[path | <pr-number> | blank for working tree] [--base <ref>] [hypothesis / focus text ...]'
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(git:*), Bash(gh:*), mcp__codex__codex
---

# `/design-challenge`

Run an adversarial design review through the `mcp__codex__codex` MCP tool. Distinct from `/codex-review` — this command challenges the **approach**, not the **correctness** of the code.

Raw slash-command arguments:
`$ARGUMENTS`

## Core constraint

- **Review-only.** Do not fix issues, apply patches, draft alternative implementations, or hint that you are about to.
- Your only job: pick the scope, hand it to Codex through one MCP call, and return Codex's output verbatim.
- No paraphrasing, no summarizing, no commentary before or after the Codex output.
- This is a **discussion artifact, not a gate.** Do not translate Codex's recommendation into a code change. Wait for the user to decide which threads to pull on.

## Argument parsing

Identical to `/codex-review`. Parse `$ARGUMENTS` in this order — first match wins:

1. **PR mode** — first token is purely numeric (e.g. `123`) or matches `^#\d+$` or is a full GitHub PR URL.
   - Normalise via `gh pr view "$ARG" --json number,title,baseRefName,headRefName -q '.'`.
   - Diff: `gh pr diff "$PR_NUM" --patch > /tmp/codex-design-challenge.patch`.
   - PR title/body becomes the **hypothesis** unless the user provides one in focus text.
   - If `gh` is missing or no GitHub remote, stop with: "PR mode requires `gh` and a GitHub remote."
2. **Path mode** — first token is a path that exists on disk.
   - If dirty (`git status --short -- <path>` non-empty), use `git diff HEAD -- <path>`; otherwise read the file(s) at their current state and review the design they embody.
3. **Branch mode** — `--base <ref>` is present.
   - Diff: `git diff "$BASE"...HEAD > /tmp/codex-design-challenge.patch`.
4. **Default — working tree mode** — no positional arg, no `--base`.
   - Combine staged + unstaged + untracked (same as `/codex-review`).

**Free-form text** after the positional arg / `--base <ref>` is treated as the **DESIGN HYPOTHESIS / FOCUS** — the author's stated approach and reasoning. Preserve verbatim. This text is the most important input to a design challenge — without it, Codex must infer the hypothesis from the diff (and will say so).

If the scoped review is empty, stop with: "Nothing to review."

## Building the prompt

Use the prompt template from the `codex:design-challenge` skill. The skill is the source of truth — fill its slots:

- `CONTEXT` — derive from PR title/body in PR mode; in local modes, prompt the user for one short sentence if the focus text doesn't already cover it (one `AskUserQuestion` round, then proceed).
- `DESIGN HYPOTHESIS` — the user's free-form text. If empty, write `<not stated — Codex must infer from SCOPE>`.
- `SCOPE` — paste the captured diff/file content inline. If it exceeds ~600 lines, list paths and let Codex read within `cwd`.
- `PROJECT CONVENTIONS` — read root `CLAUDE.md` and any nested `CLAUDE.md` files; include the "hard rules" / non-obvious sections verbatim. If none, write `<none documented>`. Also include relevant `docs/adr/*.md` filenames so Codex knows prior decisions exist.
- `FOCUS` — any free-form text that wasn't absorbed by the hypothesis slot.

Keep the CHALLENGE DISCIPLINE block and OUTPUT FORMAT block (Assumptions / Failure modes / Alternatives / Recommendation) **exactly** as written in the skill. Do not insert severity labels or merge verdicts — they belong to `/codex-review`, not here.

## Invocation

Call `mcp__codex__codex` exactly once with:

| param | value |
|---|---|
| `prompt` | The composed prompt |
| `sandbox` | `read-only` (hard default — never override from this command) |
| `approval-policy` | `never` (hard default) |
| `cwd` | Absolute path of the current working directory |
| `model` | Unset — let server default |

Never set `workspace-write` from this command. A design challenge that lets Codex write contradicts the whole framing.

## Output handling

- Return Codex's response **verbatim**. Preserve the four-section structure (Assumptions / Failure modes / Alternatives / Recommendation).
- If the MCP call fails (provider auth, network, malformed response), print the failure line(s) and stop. Do not generate a substitute critique.
- After printing, **stop**. Do not edit files, do not draft an alternative implementation, do not "helpfully" apply Codex's recommendation. The user reads, the user decides.

## Out of scope

- Background execution — MCP is synchronous; no `--wait` / `--background` flags.
- Bug hunting / severity matrix / BLOCK-APPROVE verdict — those are `/codex-review`'s job.
- Auto-iterating on the design — that's a conversation between the user and Claude, not this command's mandate.
- Posting to GitHub — out of scope.
