---
description: Multi-language code review — auto-dispatches to language-specific reviewer + always-on security review. Local uncommitted changes or GitHub PR.
argument-hint: [pr-number | pr-url | blank for local review]
---

# Code Review (multi-language dispatcher)

**Input**: $ARGUMENTS

This command auto-detects which languages are changed and dispatches in parallel to the appropriate specialist reviewer agents. **Security review always runs**, regardless of language. After review, an interactive triage flow:

1. Classifies each finding as **in-scope** or **out-of-scope** relative to this PR.
2. Auto-fixes in-scope CRITICAL / HIGH / MEDIUM; batch-asks once about LOW.
3. Offers to file `gh issue create` for out-of-scope findings.

---

## Mode Selection

If `$ARGUMENTS` contains a PR number, PR URL, or `--pr` → **PR Review Mode**.
Otherwise → **Local Review Mode**.

---

## Phase 1 — GATHER

**Environment probe (both modes):**
```bash
command -v gh >/dev/null 2>&1 && GH_OK=1 || GH_OK=0
git remote -v 2>/dev/null | grep -qiE 'github\.com' && GH_REMOTE=1 || GH_REMOTE=0
mkdir -p .claude/PRPs/reviews .claude/PRPs/followups
```
Record `GH_OK` and `GH_REMOTE` — Phase 7 / Phase 8 read them to decide whether to call `gh` or fall back to markdown. The `mkdir -p` ensures the output directories exist on first-run repos (idempotent — safe to repeat).

**Local mode:**
```bash
git diff --name-only HEAD                                   # changed files (uncommitted + staged)
git diff --unified=0 HEAD > /tmp/code-review-diff.patch     # capture once for Phase 5 hunk parsing
```
If no changed files, stop: "Nothing to review."

**PR mode:**

Normalize `$ARGUMENTS` to a PR number. `gh pr view` accepts a number, URL, or branch — let it normalize:
```bash
PR_NUM=$(gh pr view "$ARGUMENTS" --json number -q .number)
```
Then:
```bash
gh pr view "$PR_NUM" --json number,title,baseRefName,headRefName,changedFiles,mergeStateStatus,statusCheckRollup
gh pr diff "$PR_NUM" --patch > /tmp/code-review-diff.patch    # single fetch — Phase 5 reuses this
```
If PR not found, stop with error.

- If required checks are pending/failing, report and ask whether to wait or proceed anyway.
- If the PR has merge conflicts, stop and report.

Detect whether the PR head branch is checked out locally (`git branch --show-current` vs `headRefName`). Record `HEAD_CHECKED_OUT` — Phase 7 needs it to decide whether to auto-fix.

---

## Phase 2 — DETECT LANGUAGES

**Each changed file is assigned to exactly one reviewer.** Routing table:

| File matches | Assigned to |
|---|---|
| `*.py` | `python-reviewer` |
| `*.ts`, `*.tsx`, `*.js`, `*.jsx`, `*.mjs`, `*.cjs` | `typescript-reviewer` |
| `*.swift`, `Package.swift` | `swift-reviewer` |
| anything else (config, docs, shell, yaml, etc.) | `code-reviewer` (general) |

Group files by assigned reviewer. Dispatch in parallel only to reviewers that have **≥1 file** assigned. `security-reviewer` is separate from this routing — it always runs against the full file set (see Phase 3).

Example — a PR touching 5 `.py` + 1 `.yml` + 2 `.md` files dispatches three reviewers: `python-reviewer` (5 py files), `code-reviewer` (1 yml + 2 md = 3 files), `security-reviewer` (all 8 files).

---

## Phase 3 — DISPATCH (parallel)

Use the **Task tool** to spawn subagents in a single message (parallel execution):

For each matched specialist + the **mandatory security pass**, invoke:

```
Task(
  description="Python review" | "TypeScript review" | "Swift review" | "General review",
  subagent_type="python-reviewer" | "typescript-reviewer" | "swift-reviewer" | "code-reviewer",
  prompt="<diff context, changed files for this language, project conventions, repo CLAUDE.md if present>

  Required output format per finding:
    [SEVERITY] short title
    File: <path>:<line>
    Issue: <1–2 sentences>
    Fix: <concrete recommended fix>
    Scope: <optional — pre-existing | enlarged | introduced>

  Scope guidance (omit to default to mechanical diff classification):
    - pre-existing — the bug predates this PR; this PR did not touch the relevant code path.
    - enlarged — the bug existed before but this PR makes its impact worse (more callers, wider blast radius, etc.).
    - introduced — this PR introduces the bug.
  You only need to set Scope when you have a strong opinion that differs from a pure 'line falls inside the diff' check."
)

Task(
  description="Security review",
  subagent_type="security-reviewer",
  prompt="<full diff context, all changed files regardless of language, repo CLAUDE.md if present, same output format as above>"
)
```

**Rules:**
- Security review runs **every** time — never skip.
- Dispatch one Task per reviewer that has ≥1 file assigned in Phase 2.
- All Task calls go in **one message** so they execute in parallel.
- Each reviewer gets only the files routed to it in Phase 2; `security-reviewer` gets the full file set.
- File:line is **required** for every finding — Phase 5 needs it for scope classification.

---

## Phase 4 — AGGREGATE

Collect findings from all reviewer agents. Parse each finding into a structured record:

```
{ reviewer, severity, title, file, line, issue, fix, scope_hint? }
```

Merge by severity, deduplicate where the same issue is flagged by multiple reviewers. Tiebreaker for which finding to keep when two reviewers flag the same `(file, line, issue-class)`:

1. Prefer `security-reviewer` for any security-class issue (auth, secrets, injection, crypto, SSRF, etc.).
2. Otherwise prefer the language specialist (`python-reviewer`, `typescript-reviewer`, `swift-reviewer`) over the general `code-reviewer`.
3. If still tied, keep the one with the more specific `Fix:` body.

---

## Phase 5 — TRIAGE SCOPE

Classify each finding with a **two-layer rule**:

**Layer 1 — Mechanical (default):**

Parse the patch captured in Phase 1 (`/tmp/code-review-diff.patch`). For each hunk, extract `(file, line-range)` from `+++ b/<path>` and `@@ -X,Y +A,B @@` — the hunk covers lines `A..A+B-1` of the new file.

- If `B=0` (pure-deletion hunk — lines removed in old file, none added in new), the hunk contributes no in-scope lines in the new file and is skipped.
- If `B` is omitted (`@@ -X,Y +A @@`), treat as `B=1`.

For each finding, check whether `finding.file:finding.line` falls inside any hunk:
- Inside → tentative **in-scope**
- Outside → tentative **out-of-scope**

**Layer 2 — Agent override:**

If the reviewer wrote a `Scope:` line, it overrides the mechanical result:
- `Scope: pre-existing` → force **out-of-scope** (the bug predates this PR even if the line happens to be in the diff)
- `Scope: enlarged` → force **in-scope** (this PR makes it worse — fix as part of this PR)
- `Scope: introduced` → force **in-scope**

Tag every finding with its final scope and present:

```
### CRITICAL [in-scope]
[security-reviewer] SQL injection risk in src/api/users.py:88
  Issue: ...
  Fix: ...

### HIGH [in-scope]
...

### MEDIUM [out-of-scope]
[code-reviewer] Inconsistent error handling in src/utils/legacy.py:301
  Scope: pre-existing — this PR did not touch this file
  Issue: ...
  Fix: ...

### LOW [in-scope]
...
```

---

## Phase 6 — DECIDE (verdict, in-scope only)

Out-of-scope findings do not block merge — they go through Gate B in Phase 7.

| Condition (in-scope only) | Decision |
|---|---|
| Zero CRITICAL/HIGH | **APPROVE** |
| HIGH issues only | **WARNING** (merge with caution) |
| Any CRITICAL | **BLOCK** — must fix before merge |

Report the verdict and severity counts (split in-scope vs out-of-scope):

```
## Code Review

**Reviewers:** python-reviewer, security-reviewer
**Files:** 7 changed (5 .py, 2 .yml)

| Severity | In-scope | Out-of-scope |
|---|---|---|
| CRITICAL | 1 | 0 |
| HIGH | 2 | 1 |
| MEDIUM | 3 | 2 |
| LOW | 4 | 0 |

**Verdict:** BLOCK — 1 CRITICAL in-scope must be fixed before merge.
```

---

## Phase 7 — APPLY

### Gate A — fix decisions (in-scope only)

- **In-scope CRITICAL / HIGH / MEDIUM** → auto-fix without asking. After each fix, state one line: `fixed: <title> (<file>:<line>)`.
- **In-scope LOW** → one batch question via `AskUserQuestion`:
  - Header: `Fix LOW nits`
  - Question: `Found N LOW-severity nits in this PR. Fix them all?`
  - Options: `Yes, fix all` / `No, skip all`

After applying fixes, run `git diff --stat` and report what changed.

**Skip auto-fix when** the PR head is not the currently checked-out branch (PR Review Mode reviewing someone else's PR). Print: `Skipping auto-fix — PR branch is not checked out. Findings reported only.` and proceed to Phase 8.

### Gate B — out-of-scope handling

If there are any out-of-scope findings, ask once via `AskUserQuestion`:
- Header: `Track out-of-scope?`
- Question: `Found M out-of-scope findings (pre-existing issues this PR did not introduce). Create issues to track?`
- Options: `Yes, create all` / `No, skip all`

**Destination is decided by Phase 1 probes** — no per-issue branching:

- `GH_OK=1` AND `GH_REMOTE=1` → use `gh issue create` for each finding.
- Otherwise → write each finding to `.claude/PRPs/followups/<YYYYMMDD-HHMM>-<slug>.md` and warn:
  > `gh` or GitHub remote not detected. Saved N follow-ups to `.claude/PRPs/followups/`. Migrate to your issue tracker manually.

`gh issue create` invocation:
```bash
gh issue create \
  --title "[code-review] <severity>: <short title>" \
  --body "$(cat <<'EOF'
**Discovered while reviewing**: <PR #N | local branch <name>>
**Severity**: <severity>
**File**: <file>:<line>
**Reviewer**: <reviewer-name>

## Issue
<issue body>

## Suggested fix
<fix body>
EOF
)" \
  --label "tech-debt,code-review"
```

If `gh issue create` errors with `could not add label: 'tech-debt' not found in repository`, retry once without `--label` and warn the user that the labels don't exist on the repo. Report each created issue URL.

---

## Phase 8 — PUBLISH (PR mode only, requires GH_OK=1)

Save the post-triage report to `.claude/PRPs/reviews/pr-<PR_NUM>-review.md`. The report MUST include **both verdicts** side by side so the audit trail is clear:

```
Pre-fix verdict (Phase 6):  BLOCK   — 1 CRITICAL, 2 HIGH in-scope
Post-fix verdict (Phase 8): APPROVE — 0 CRITICAL, 0 HIGH unfixed
```

The post-fix verdict is computed by re-running the Phase 6 matrix against **remaining unfixed in-scope findings** (everything in Gate A LOW that the user said "skip", plus any in-scope finding that was deferred because Gate A was skipped — see edge case below).

Map post-fix verdict → `gh pr review` action. The mapping is aligned with the Phase 6 matrix:

| Post-fix verdict | gh action | Rationale |
|---|---|---|
| APPROVE (zero CRITICAL/HIGH unfixed) | `gh pr review <PR_NUM> --approve --body "<summary>"` | Matches Phase 6 APPROVE |
| WARNING (HIGH only unfixed) | `gh pr review <PR_NUM> --comment --body "<summary, advisory>"` | Matches Phase 6 WARNING ("merge with caution") — do **not** post `--request-changes` for HIGH-only since the matrix says it's not a hard block |
| BLOCK (any CRITICAL unfixed) | `gh pr review <PR_NUM> --request-changes --body "<summary with required fixes>"` | Matches Phase 6 BLOCK |

The only realistic way to land at WARNING or BLOCK post-fix is when Gate A was skipped (PR head not checked out — see edge case in Phase 7). In normal flow, all CRITICAL/HIGH/MEDIUM are auto-fixed and the post-fix verdict is APPROVE.

Inline per-line review comments are out of scope for v1 — summary review body only. (Posting inline comments requires building the full `POST /repos/{owner}/{repo}/pulls/{n}/reviews` body with `commit_id` + `comments[]`, which is non-trivial. Track as follow-up if needed.)

---

## Edge Cases

- **No `gh` CLI** (`GH_OK=0`) — PR mode is unavailable; stop with: "PR review requires `gh`. Install or use local mode." Gate B writes markdown follow-ups regardless of mode.
- **No GitHub remote** (`GH_REMOTE=0`) — PR mode unavailable for the same reason. Gate B writes markdown follow-ups.
- **Diverged branches** → suggest `git fetch origin && git rebase origin/<base>` before review.
- **Large PRs (>50 files)** → warn about scope. Run dispatch normally but flag in summary.
- **Mixed-language PR with shared config (e.g. monorepo)** → multiple specialists run in parallel, each on its slice.
- **Only docs / markdown changed** → run `code-reviewer` (general) + `security-reviewer` (still scans for accidental secrets in markdown).
- **Reviewing someone else's PR (head branch not checked out)** — Phase 7 Gate A is **skipped** entirely (the user can't apply edits to a branch they don't have). Gate B still runs and files follow-ups. Phase 8 then computes the post-fix verdict against the full in-scope set (since nothing was fixed) — by construction this equals the Phase 6 verdict. Both verdicts go into the saved artifact so the audit trail is honest.
- **Finding without a parseable `file:line`** — Phase 5 treats it as `out-of-scope` (cannot verify it falls in the diff). It flows into Gate B with the reviewer's verbatim text in the issue body. Apply uniformly inside Phase 5, not as a separate special case.
- **Non-interactive run** (e.g. Claude Code invoked from a CI hook with no `AskUserQuestion` channel) — default Gate A LOW to **skip** and Gate B to **skip**. Both are reversible — the user can re-run interactively to capture them.
- **Empty PR / zero findings** — skip Phases 5–7. Phase 8 posts `gh pr review --approve --body "Automated review found no issues."` if in PR mode; in local mode just print "Nothing to fix."
