---
description: Multi-language code review — auto-dispatches to language-specific reviewer + always-on security review. Local uncommitted changes or GitHub PR.
argument-hint: [pr-number | pr-url | blank for local review]
---

# Code Review (multi-language dispatcher)

**Input**: $ARGUMENTS

This command auto-detects which languages are changed and dispatches in parallel to the appropriate specialist reviewer agents. **Security review always runs**, regardless of language.

---

## Mode Selection

If `$ARGUMENTS` contains a PR number, PR URL, or `--pr` → **PR Review Mode**.
Otherwise → **Local Review Mode**.

---

## Phase 1 — GATHER

**Local mode:**
```bash
git diff --name-only HEAD       # uncommitted + staged
git diff --name-only --cached   # staged only
```
If no changed files, stop: "Nothing to review."

**PR mode:**
```bash
gh pr view <NUMBER> --json number,title,baseRefName,headRefName,changedFiles
gh pr diff <NUMBER> --name-only
```
If PR not found, stop with error.

Before reviewing a PR, check merge readiness:
```bash
gh pr view <NUMBER> --json mergeStateStatus,statusCheckRollup
```
- If required checks are pending/failing, report and ask whether to wait or proceed anyway.
- If the PR has merge conflicts, stop and report.

---

## Phase 2 — DETECT LANGUAGES

Classify changed files by extension:

| Extension(s) | Specialist agent |
|---|---|
| `*.py` | `python-reviewer` |
| `*.ts`, `*.tsx`, `*.js`, `*.jsx`, `*.mjs`, `*.cjs` | `typescript-reviewer` |
| `*.swift`, `Package.swift` | `swift-reviewer` |
| anything else (or in addition) | `code-reviewer` (general) |

A single PR can hit multiple specialists — dispatch to **all** that match, in parallel.

---

## Phase 3 — DISPATCH (parallel)

Use the **Task tool** to spawn subagents in a single message (parallel execution):

For each matched specialist + the **mandatory security pass**, invoke:

```
Task(
  description="Python review" | "TypeScript review" | "Swift review" | "General review",
  subagent_type="python-reviewer" | "typescript-reviewer" | "swift-reviewer" | "code-reviewer",
  prompt="<diff context, changed files for this language, project conventions, repo CLAUDE.md if present>"
)

Task(
  description="Security review",
  subagent_type="security-reviewer",
  prompt="<full diff context, all changed files regardless of language, repo CLAUDE.md if present>"
)
```

**Rules:**
- Security review runs **every** time — never skip.
- If no language specialist matches (e.g. only config / markdown / shell changed), fall back to `code-reviewer` general agent + `security-reviewer`.
- All Task calls go in **one message** so they execute in parallel.
- Each specialist gets only the files in its language; security gets the full set.

---

## Phase 4 — AGGREGATE

Collect findings from all reviewer agents. Merge by severity, deduplicate where the same issue is flagged by multiple reviewers (e.g. a hardcoded secret flagged by both `python-reviewer` and `security-reviewer`).

Output format:

```
## Code Review

**Reviewers:** python-reviewer, security-reviewer
**Files:** 7 changed (5 .py, 2 .yml)

### CRITICAL
[python-reviewer] Hardcoded API key in src/api/client.py:42
  Issue: ...
  Fix: ...

[security-reviewer] SQL injection risk in src/api/users.py:88
  Issue: ...
  Fix: ...

### HIGH
[python-reviewer] Bare except in src/utils/loader.py:120
  ...

### MEDIUM
...

### LOW
...

## Summary

| Severity | Count | Status |
|---|---|---|
| CRITICAL | 2 | block |
| HIGH | 3 | warn |
| MEDIUM | 5 | info |
| LOW | 2 | note |

**Verdict:** BLOCK — 2 CRITICAL must be fixed before merge.
```

---

## Phase 5 — DECIDE

| Condition | Decision |
|---|---|
| Zero CRITICAL/HIGH issues | **APPROVE** |
| HIGH issues only | **WARNING** (merge with caution) |
| Any CRITICAL issues | **BLOCK** — must fix before merge |

---

## Phase 6 — PUBLISH (PR mode only)

For PR review mode, save artifact and post to GitHub:

Save to `.claude/PRPs/reviews/pr-<NUMBER>-review.md` with the aggregated report.

Post to GitHub:
```bash
# APPROVE
gh pr review <NUMBER> --approve --body "<summary>"

# REQUEST CHANGES (HIGH issues)
gh pr review <NUMBER> --request-changes --body "<summary with required fixes>"

# COMMENT (draft PR or informational)
gh pr review <NUMBER> --comment --body "<summary>"
```

For inline line comments, use the GitHub review API with the head commit SHA:
```bash
gh api "repos/{owner}/{repo}/pulls/<NUMBER>/reviews" \
  -f event="COMMENT" \
  -f body="<overall summary>" \
  --input comments.json  # [{"path": "file", "line": N, "body": "comment"}, ...]
```

---

## Edge Cases

- **No `gh` CLI in PR mode** → fall back to local review of `git fetch && git diff <base>...HEAD`. Warn user.
- **Diverged branches** → suggest `git fetch origin && git rebase origin/<base>` before review.
- **Large PRs (>50 files)** → warn about scope. Run dispatch normally but flag in summary.
- **Mixed-language PR with shared config (e.g. monorepo)** → multiple specialists run in parallel, each on its slice.
- **Only docs / markdown changed** → run `code-reviewer` (general) + `security-reviewer` (still scans for accidental secrets in markdown).
