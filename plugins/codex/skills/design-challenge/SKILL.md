---
name: design-challenge
description: Challenge an implementation approach or design choice via Codex MCP. Read-only, asks "is this the right path?" — not "are there bugs?". Trigger when the user says "质疑这个方案" / "这个设计靠不靠谱" / "challenge this design" / "design review" / "second-guess this approach" / "考虑过 X 吗" / "is this the right approach" / "stress-test the design" / "punch holes in this". Returns assumptions / failure modes / alternatives — NOT a bug list, NOT a severity matrix.
---

# Design Challenge (MCP)

The companion to `codex:codex-review`. Where codex-review asks **"is this code correct?"**, this skill asks **"is this approach right?"** — surfacing assumptions, hidden coupling, and real-world failure modes the author may not have considered.

## When to use

- User explicitly wants a design critique, not a bug hunt (中: "质疑一下这个方案" / "punch holes" / "second opinion on the approach" / "我这么做对吗").
- You finished a non-trivial design decision and want adversarial pushback before committing — **ask the user first**.
- The change is high-stakes (security boundary, migration, payment flow, API contract) and the user wants the "are we sure?" pass.

## When NOT to use

- Plain defect hunting → `codex:codex-review` instead.
- Refactor / rename / mechanical change → no design surface to challenge; skip both.
- Drafting code from scratch → premature; do it after a real proposal exists.

## codex-review vs. design-challenge

Both run Codex via MCP, read-only. They differ in what they look for:

| | `codex-review` | `design-challenge` |
|---|---|---|
| Asks | "Are there bugs?" | "Is this the right approach?" |
| Looks at | Behavior, security, edge cases | Assumptions, tradeoffs, alternatives |
| Output | Severity ladder + BLOCK/APPROVE | Assumption list + failure modes + alternatives |
| Gate-ready? | Yes (verdict drives merge decision) | No (discussion artifact, not a gate) |
| Best paired with | Pre-merge | Pre-implementation, or before doubling down |

Chain pattern (rare, high-stakes only): `design-challenge` → reach alignment on approach → implement → `codex-review` before merge.

## Invocation

Make exactly one `mcp__codex__codex` call with:

| param | value |
|---|---|
| `prompt` | The challenge brief (template below) |
| `sandbox` | `read-only` |
| `approval-policy` | `never` |
| `cwd` | Absolute path of the current working directory |
| `model` | Unset unless the user named one |

`sandbox=read-only` + `approval-policy=never` is a **hard** default. Never override from this skill — challenging a design that's not yet implemented does not need write access. If the user wants Codex to draft an alternative implementation, use `codex:codex-rescue` instead.

## Prompt template

Codex hasn't seen your conversation. Brief it cold and force adversarial framing:

```
You are an adversarial design reviewer. I'm Claude Code on the same
codebase and the user wants you to challenge an implementation approach
or design choice. Your job is NOT to find bugs in code that already
exists — it is to ask whether the chosen approach is the right one and
where it could fail in the real world.

Output is read-only. Do not edit files. Do not produce a code patch.

CONTEXT (what + why):
  <1–3 sentences: what is being designed/changed, what problem it solves>

DESIGN HYPOTHESIS (the author's chosen approach + reasoning):
  <The user's stated approach. If they didn't state one, derive it from
   the diff/files in SCOPE — but call out that you had to infer it.>

SCOPE (code that embodies or is affected by the hypothesis):
  <paths / line ranges / inline diff. Smaller is better — this is a
   conceptual review, not a line-by-line audit.>

PROJECT CONVENTIONS (if any):
  <CLAUDE.md hard rules, prior ADRs, architectural decisions>

FOCUS (optional, user's specific concern):
  <free-form, verbatim>

CHALLENGE DISCIPLINE — apply all of these:

1. Surface implicit assumptions the design depends on. List each
   one explicitly. The author has not stated them; that is the gap
   you are filling. Be specific — "the database will be reachable"
   is too generic; "the migration completes inside the 30s Railway
   pre-deploy window even with the 50M-row backfill" is useful.

2. For each assumption, name at least one realistic scenario where
   it could be false. Prefer scenarios that have actually happened
   in similar systems (race conditions under concurrent writes,
   provider outages, schema drift, retry storms, third-party rate
   limits, etc.) over abstract "what-ifs".

3. Identify hidden coupling: places where this design implicitly
   relies on behavior outside its own scope (a sibling service's
   ordering guarantees, a shared mutex, a not-yet-documented invariant,
   the order of middleware, a specific framework version's quirk).

4. Propose 1–3 alternative approaches that handle the same problem
   differently. For each, state in one line what tradeoff it makes
   relative to the hypothesis (more complex but safer / simpler but
   loses property X / cheaper to implement but harder to evolve).

5. Be honest about residual risk. If the design is actually fine for
   the stated constraints, say so — but list which constraints, so
   the reader knows what the verdict depends on.

Do NOT:
  - List bugs unless they are direct evidence that an assumption is broken.
  - Use severity labels (CRITICAL / HIGH / etc.) — this isn't a gate.
  - Issue a merge verdict (APPROVE / BLOCK) — this isn't a gate.
  - Suggest mechanical refactors. The question is "is the approach right?",
    not "is the code clean?".

OUTPUT FORMAT — four sections, in this order:

  ## Assumptions
  - <numbered list, each one a specific assumption the design depends on>

  ## Failure modes
  - <for each assumption, the scenario where it could fail>

  ## Alternatives considered
  - <1–3 alternative approaches + the tradeoff each makes>

  ## Recommendation
  <one paragraph: stick with the hypothesis / iterate before committing /
   reconsider. State which constraints the recommendation depends on.>

If you genuinely cannot find anything to challenge, say so in the
Recommendation section — but list what assumptions you DID consider,
so the reader can see the coverage of the all-clear.
```

## After the call

- Preserve Codex's section structure (Assumptions → Failure modes → Alternatives → Recommendation) verbatim.
- This is a **discussion artifact, not a gate.** Do not treat it as merge approval/rejection. Do not auto-apply any of its suggestions. Wait for the user to decide which threads to pull on.
- If the user wants to iterate the design after reading it, that's a design conversation — not a code edit. Help them think; don't start writing the alternative.
- If the MCP call fails or returns malformed output, report verbatim and stop. Do not generate a substitute design critique.

## What this skill is NOT

- Not `codex:codex-review` — that's the bug-hunt path. See the table above.
- Not `codex:codex-rescue` — that's "Claude is stuck, hand off to Codex to implement". This is review-only.
- Not the place to call `setup`, `cancel`, `status`, `result`. Those live in the upstream `openai-codex` plugin's slash commands.
