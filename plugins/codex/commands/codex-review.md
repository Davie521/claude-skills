---
description: Codex code review via MCP — severity-tagged findings, read-only, single round-trip. Local diff, file/dir, or GitHub PR.
argument-hint: '[path | <pr-number> | blank for working tree] [--base <ref>] [focus text ...]'
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(git:*), Bash(gh:*), mcp__codex__codex
---

# `/codex-review`

Run a Codex code review through the `mcp__codex__codex` MCP tool. The companion CLI is not involved — this is a single MCP round-trip.

Raw slash-command arguments:
`$ARGUMENTS`

## Core constraint

- **Review-only.** Do not fix issues, apply patches, or hint that you are about to.
- Your only job: pick the scope, hand it to Codex through one MCP call, and return Codex's output verbatim.
- No paraphrasing, no summarizing, no commentary before or after the Codex output.
- If Codex returns findings, do not "helpfully" start applying them. The user will say what to fix.

## Argument parsing

Parse `$ARGUMENTS` in this order — first match wins:

1. **PR mode** — first token is purely numeric (e.g. `123`) or matches `^#\d+$` or is a full GitHub PR URL.
   - Run `gh pr view "$ARG" --json number,title,baseRefName,headRefName -q '.'` to normalise.
   - Run `gh pr diff "$PR_NUM" --patch > /tmp/codex-review-diff.patch`.
   - If `gh` is not installed or no GitHub remote, stop with: "PR mode requires `gh` and a GitHub remote."
2. **Path mode** — first token is a path that exists on disk (file or directory).
   - Collect the path(s). If the path is dirty (`git status --short -- <path>` non-empty), use `git diff HEAD -- <path>` for the diff; otherwise read the file(s) at their current state and review them as a whole.
3. **Branch mode** — `--base <ref>` is present.
   - Diff: `git diff "$BASE"...HEAD > /tmp/codex-review-diff.patch`.
4. **Default — working tree mode** — no positional arg, no `--base`.
   - Combine staged + unstaged + untracked. Equivalent to:
     - `git diff --cached > /tmp/codex-review-diff.patch`
     - `git diff >> /tmp/codex-review-diff.patch`
     - For each untracked file from `git status --short --untracked-files=all | awk '$1 == "??" { $1=""; print }'`, append a synthetic `diff --git /dev/null <path>` block.

**Free-form focus text** — anything after the positional arg / `--base <ref>` that is not a recognised flag is the user's focus hint. Preserve it verbatim and pass into the Codex prompt under a `FOCUS:` line.

If the scoped review is empty (no staged/unstaged/untracked, or `gh pr diff` is empty), stop with: "Nothing to review."

## Building the prompt

Use the prompt template from the `codex:codex-review` skill. The skill is the source of truth — don't duplicate the template here, just fill its slots:

- `CONTEXT (what + why)` — derive from the PR title/body in PR mode; in local modes, leave it for the user's focus text or `<not provided>` if absent.
- `SCOPE TO REVIEW` — paste the captured diff/file content inline. If the diff exceeds ~600 lines, list the changed file paths and tell Codex it may read them within `cwd`.
- `PROJECT CONVENTIONS` — read the repo's `CLAUDE.md` (root + any nested) and include the "hard rules" / non-obvious conventions section verbatim. If no `CLAUDE.md`, write `<none documented>`.
- `FOCUS` — the user's free-form text, verbatim.
- Keep the REVIEW DISCIPLINE block (severity ladder + security pass + scope tagging + file:line) and OUTPUT FORMAT block exactly as written in the skill.

## Invocation

Call `mcp__codex__codex` exactly once with:

| param | value |
|---|---|
| `prompt` | The composed prompt |
| `sandbox` | `read-only` (hard default — never override from this command) |
| `approval-policy` | `never` (hard default) |
| `cwd` | Absolute path of the current working directory |
| `model` | Unset — let server default |

Do **not** set `workspace-write` or `on-request` from `/codex-review` — that's a different workflow. If the user wants Codex to actually edit, they should use `/codex:rescue` (upstream) or `codex:codex-rescue` subagent.

## Output handling

- Return Codex's response **verbatim**. No reformat, no commentary, no "here's what I found" preamble.
- If the MCP call fails (provider auth, network, malformed response), print the failure line(s) and stop. Do not invent findings to fill the gap.
- After printing, **stop**. Do not edit any files. Do not announce a follow-up. Wait for the user.

## Out of scope

- Background execution — MCP is synchronous and the round-trip is short. No `--wait` / `--background` flags.
- `/codex:status` job tracking — this command does not register a companion job. To see history, the user should switch to `/codex:review` (upstream).
- Auto-fixing — see Core constraint.
- Posting to GitHub (`gh pr review`) — out of scope for v1.
