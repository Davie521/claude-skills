---
name: codex-review
description: Default code review route — runs Codex via MCP with the multi-language code-review methodology (severity matrix, file:line, scope triage, mandatory security pass). Read-only, no edits. Trigger when the user says "code review" / "审一下" / "review 一下" / "审这个 diff" / "用 codex 审" / "second opinion" / "复审" / "看看这次改动" or asks for any code review on a diff, file, or PR. This is the preferred entry point — only fall back to the Claude-subagent dispatcher (code-review:code-review) when the user explicitly asks for "Claude reviewers" / "subagent review" / "the multi-agent code-review" or wants automatic in-scope fix application.
---

# Codex Review (MCP)

The **default** code review route for this user. Codex sees the code without Claude's prior assumptions and reports back through a single MCP round-trip. Read-only by hard default.

## When to use

- User says any of: "code review" / "审一下" / "review 一下" / "审这个 diff" / "复审" / "看看这次改动" / "用 codex 审" / "second opinion" → run this skill.
- You just wrote something non-trivial and want an independent pass before declaring done — **ask the user first**, don't auto-trigger.

## Routing vs. `code-review:code-review`

The Claude-subagent dispatcher (`/code-review`) still exists, but is **not** the default. Use it only when:

- User explicitly asks for "Claude reviewers" / "subagent review" / "the multi-agent code-review".
- User wants automatic in-scope fix application (this skill never edits).
- User wants the artifact written to `.claude/PRPs/reviews/` or auto-posted via `gh pr review`.

**Chain pattern (optional, high-stakes work only)**: `/code-review` → apply fixes → `codex-review` as adversarial verification before merge. Mirrors `quality:santa-method`. Don't chain by default.

## Invocation

Make exactly one `mcp__codex__codex` call with:

| param | value |
|---|---|
| `prompt` | The review brief (see template below) |
| `sandbox` | `read-only` |
| `approval-policy` | `never` |
| `cwd` | The current working directory (absolute path) |
| `model` | Leave unset unless the user explicitly named one |

`sandbox=read-only` + `approval-policy=never` is a hard default. Override **only** if the user explicitly says "let codex edit / fix it" — in that case raise to `workspace-write` + `on-request` and confirm scope before calling.

## Prompt template

Codex hasn't seen your conversation, so brief it cold and embed the review discipline. This template mirrors the methodology in `code-review:code-review` (severity matrix, file:line, scope triage, security pass) — collapsed into a single prompt:

```
You are reviewing a code change with the same rigor as a senior engineer
gating a merge. I'm Claude Code on the same codebase; you are an
independent reviewer. Output is read-only — do not edit files.

CONTEXT (what + why):
  <1–3 sentences>

SCOPE TO REVIEW:
  <paths / line ranges / inline diff. Small diffs: paste verbatim.
   Larger: list paths and let Codex read.>

PROJECT CONVENTIONS (if any):
  <CLAUDE.md hard rules, naming, security gates, migration rules>

REVIEW DISCIPLINE — apply all of these:

1. Severity ladder (use exactly these labels, no others):
     CRITICAL — security hole, data loss, prod breakage, payments
                / auth / migration correctness
     HIGH     — likely bug under normal use, perf cliff, broken
                contract with a known caller
     MEDIUM   — incorrect-but-unlikely path, missing edge case,
                hidden coupling that will bite later
     LOW      — quality / readability / minor robustness
     NIT      — style only; safe to defer

2. Security pass is mandatory. Even if the diff looks innocuous,
   explicitly scan for: secret leakage, SQL injection, SSRF, unsafe
   deserialization, missing authz, broken crypto, log injection,
   path traversal, race conditions in auth-adjacent code. If clean,
   say so explicitly in a one-line "Security: clean — checked X, Y, Z".

3. Scope tagging per finding:
     introduced   — this diff added the bug
     enlarged     — bug pre-existed but this diff widens its blast radius
     pre-existing — bug predates this diff; called out for awareness only
   Default to "introduced" if uncertain. Pre-existing findings go last.

4. File:line is required for every finding. Quote the offending
   snippet (≤3 lines) when it disambiguates.

OUTPUT FORMAT — one block per finding, ordered by severity then scope:

  [SEVERITY] <short title>           (Scope: introduced|enlarged|pre-existing)
  File:    <path>:<line>
  Issue:   <1–2 sentences>
  Fix:     <concrete recommended fix; "looks correct" is allowed only
            when you also explain why a tempting alternative is wrong>

End with a one-line verdict using this matrix:
  any CRITICAL                       → BLOCK
  HIGH-only (introduced or enlarged) → WARNING — merge with caution
  zero CRITICAL/HIGH introduced      → APPROVE

If you find nothing, say "No findings." then list the highest-risk
areas you DID scrutinise so the user knows what the all-clear covers.
Do not pad the report with restatement of the diff.
```

## After the call

Apply the same rules as the `codex-result-handling` skill in the upstream plugin:

- Preserve Codex's severity ordering, file paths, and line numbers verbatim.
- Preserve evidence boundaries — if Codex marked something as inference or open question, keep that label.
- **STOP after presenting findings.** Do not apply fixes. Ask the user which findings, if any, to fix. Auto-fixing from a review is forbidden, even for "obvious" ones — that's the whole point of an independent review.
- If Codex reported no findings, say so directly and include its "highest-risk area scrutinised" note so the user can judge coverage.
- If the MCP call failed (auth error, sandbox violation, malformed response), report the failure verbatim and stop. Do not generate a substitute review yourself.

## What this skill is NOT

- Not `codex:codex-rescue` — that's for "Claude is stuck, hand off to Codex to implement". This is review-only.
- Not the place to call `setup`, `cancel`, `status`, `result`. Those live in the upstream `openai-codex` plugin's slash commands.
