---
name: to-prd
description: Turn the current conversation context into a PRD and publish it to the project issue tracker (or save as a markdown file). Use when user wants to create a PRD from the current context.
---

This skill takes the current conversation context and codebase understanding and produces a PRD. **Do NOT interview the user** — just synthesize what you already know. If the conversation has not produced enough context yet, say so explicitly and suggest `/grill-with-docs` first; do not start interviewing from this skill.

## Process

1. **Domain glossary check.** Before drafting the PRD:

   - If the project has a `CONTEXT.md` / domain glossary, read it and use the glossary's vocabulary throughout the PRD.
   - **If `CONTEXT.md` does NOT exist, surface this once** — say: "No `CONTEXT.md` yet. The PRD will use the most domain-precise terms I can extract from the conversation; want me to also seed a `CONTEXT.md` with the 3-5 load-bearing terms before publishing?" Don't block — proceed if AFK.
   - If `docs/adr/` exists, respect any ADRs in the area you're touching.

2. **Sketch the major modules** you will need to build or modify to complete the implementation. Actively look for opportunities to extract deep modules that can be tested in isolation.

   A deep module (as opposed to a shallow module) is one which encapsulates a lot of functionality in a simple, testable interface which rarely changes. (See `improve-codebase-architecture/LANGUAGE.md` for the full vocabulary.)

   Check with the user that these modules match their expectations. Check with the user which modules they want tests written for.

3. **Write the PRD** using the template below, then publish it:

   - **If the repo has GitHub configured (`gh auth status` succeeds)**: publish as a GitHub issue.
   - **Otherwise**: save to `docs/prds/PRD-{slug}.md` and tell the user the path.

   If a triage label vocabulary is configured (e.g. `ready-for-agent`), apply it. Otherwise, no label.

<prd-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this PRD.

## Further Notes

Any further notes about the feature.

</prd-template>

## Use with

- `grill-with-docs` — the *interview* counterpart to this skill. Run grill-with-docs first when the conversation hasn't established enough context; run `to-prd` to crystallise that context once it has.
- `blueprint` — once the PRD is published, run `blueprint` to break it into a multi-PR construction plan.
- `architecture-decision-records` — if the PRD's Implementation Decisions contain hard-to-reverse architectural choices, those should also become ADRs (use this skill to detect and write them).

## Origin

Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) — `engineering/to-prd`. License: MIT.
