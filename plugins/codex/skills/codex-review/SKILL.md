---
name: codex-review
description: Default code review route — runs Codex (read-only `codex exec` via the codex-run wrapper) with the multi-language code-review methodology (severity matrix, file:line, scope triage, mandatory security pass). Read-only, no edits. Trigger when the user says "code review" / "审一下" / "review 一下" / "审这个 diff" / "用 codex 审" / "second opinion" / "复审" / "看看这次改动" or asks for any code review on a diff, file, or PR. This is the preferred entry point — route to the built-in /code-review skill when the user wants inline PR comments (--comment) or the findings auto-applied (--fix), and to the Claude-subagent dispatcher (code-review:code-review) only when the user explicitly asks for "Claude reviewers" / "subagent review" / "the multi-agent code-review".
---

# Codex Review

The **default** code review route for this user. Codex sees the code without Claude's prior assumptions and reports back from a single read-only `codex exec` run. Read-only by hard default.

## When to use

- User says any of: "code review" / "审一下" / "review 一下" / "审这个 diff" / "复审" / "看看这次改动" / "用 codex 审" / "second opinion" → run this skill.
- You just wrote something non-trivial and want an independent pass before declaring done — **ask the user first**, don't auto-trigger.

## Routing — three review skills, one default

Three review routes coexist; this skill is the default. Pick by what the user needs:

| Route | Use when |
|---|---|
| **`codex-review` (this skill)** | Default for any "code review" request — external second opinion from a non-Claude model, read-only |
| **Built-in `code-review` skill** | User wants findings posted as **inline PR comments** (`--comment`) or **auto-applied to the working tree** (`--fix`) — the only route of the three that can do either |
| **`code-review:code-review` (plugin dispatcher)** | User explicitly asks for "Claude reviewers" / "subagent review" / "the multi-agent code-review" — Claude language-expert subagents (python/swift/typescript/security) |

Additional reasons to pick the plugin dispatcher (`code-review:code-review`):

- User wants automatic in-scope fix application (this skill never edits).
- User wants the artifact written to `.claude/PRPs/reviews/` or auto-posted via `gh pr review`.

**Chain pattern (optional, high-stakes work only)**: `/code-review` → apply fixes → `codex-review` as adversarial verification before merge. Mirrors `quality:santa-method`. Don't chain by default.

## Invocation

Codex removed `codex mcp-server` in 0.154.0, so there is no MCP tool any more.
Run exactly one review through the `codex-run` wrapper (`~/.local/bin/codex-run`):

1. `D=$(mktemp -d "${TMPDIR:-/tmp}/codex-review.XXXXXX")` — one scratch dir per review.
2. Write the review brief (template below) to `$D/prompt.md` with the Write tool —
   not a heredoc, diffs contain quotes and `$`.
3. Run with the Bash tool, **`run_in_background: true`**:
   `codex-run <absolute cwd> "$D/prompt.md" "$D"`
   Add `--model <name>` only if the user named a model. Reviews take minutes
   (median ~7 min, up to ~17), past the 10-minute foreground Bash limit — so never
   run it in the foreground. Wait for the completion notification, then read the
   task output.
4. Exit code decides what happened — **not** whether text came back:

| exit | meaning | do |
|---|---|---|
| `0` | review finished; the report follows the `-----` line | present it (see After the call) |
| `3` | Codex reported errors (usage limit, auth, bad model) — the wrapper prints them | report verbatim, stop |
| `124` | hit `CODEX_RUN_MAX_SECS` (default 2400 s) | report, stop; offer a rerun at a lower `--effort` |
| `90` | no codex with `--ignore-user-config` on this machine | report, stop |
| other | codex crashed — wrapper prints stderr tail | report verbatim, stop |

What the wrapper fixes for you, so do not re-add these by hand:

- `--ignore-user-config`: `~/.codex/config.toml` is skipped, so the user's own
  Codex MCP servers (blender, node_repl…) are not spawned and its global
  `sandbox_mode = "danger-full-access"` cannot leak into a review.
- `-s read-only` and `--skip-git-repo-check` (reviews of non-git paths work).
- Model = `codex-best-model`, effort = `codex-best-model --effort` (see below).
- Success is judged from the event stream: Codex exits 0 even when every tool
  call inside the run failed, so the wrapper requires no `error` / `turn.failed`
  events, a `turn.completed` event and a non-empty final answer.

Artifacts stay in `$D` (`last.md`, `events.jsonl`, `stderr.log`) for debugging.

**Run reviews at the model's ceiling.** `codex-best-model --effort` prints the
highest level the selected model supports, so model and effort always match:
today that resolves to `ultra` on `gpt-6-astra`. Do not hardcode `ultra` — not
every model reaches it (`gpt-5.5` stops at `xhigh`, `gpt-5.6-luna` at `max`),
and passing a level the model does not list is a silent-downgrade risk once the
auto-selected flagship changes. The wrapper falls back to `max` if the command
fails; pass `--effort <level>` only when the user asks for a lighter run.

`ultra` is "maximum reasoning with automatic task delegation" — the model may
fan work out to sub-tasks. Budget for it: reviews already ran ~7–8 min at the
median on `max`, and a `max`-level review has hit the plan usage limit
mid-report before. A review that dies partway with a usage-limit error is that
expected failure mode, not a broken skill — rerun later or drop one level.

**Picking the model.** `codex-run` calls `codex-best-model` and passes its stdout as the model.
It reads `~/.codex/models_cache.json` — the catalog the Codex CLI refreshes on
its own — and prints the `visibility: "list"` entry with the lowest `priority`,
which is OpenAI's own ranking with `1` as most capable. A newly shipped
flagship is therefore picked up automatically, with nothing to edit here. Add
`-v` for priority and catalog age on stderr.

Do **not** hardcode a slug in this file: that silently keeps reviews on an
ageing model after a better one ships. If `codex-best-model` exits non-zero,
the wrapper omits the model and Codex uses its built-in default — never guess a
model name. Never pass a `visibility: "hide"` model such as `gpt-reserve` or
`codex-auto-review`; those are internal to Codex.

Read-only is a hard default and `codex-run` has no write mode. If the user explicitly says "let codex edit / fix it", that is not this skill — confirm scope with the user and hand off to `codex:codex-rescue`.

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
- If `codex-run` exited non-zero (usage limit, auth error, timeout, crash), report its output verbatim and stop. Do not generate a substitute review yourself.

## What this skill is NOT

- Not `codex:codex-rescue` — that's for "Claude is stuck, hand off to Codex to implement". This is review-only.
- Not the place to call `setup`, `cancel`, `status`, `result`. Those live in the upstream `openai-codex` plugin's slash commands.
