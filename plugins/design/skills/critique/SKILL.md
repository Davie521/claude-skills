---
name: critique
description: Evaluate design from a UX perspective, assessing visual hierarchy, information architecture, emotional resonance, cognitive load, and overall quality with quantitative scoring, persona-based testing, and actionable feedback. Use when the user asks to review, critique, evaluate, 评审, or give feedback on a design or component. Diagnosis only — critique judges whether the experience works; to produce or modify a design, use ui-ux-pro-max.
user-invocable: true
argument-hint: "[area (feature, page, component...)]"
---

## PREPARATION

Gather two things before critiquing — do not block on them, infer and state your assumption if unavailable:

1. **What the interface is trying to accomplish** — ask the user if it isn't obvious.
2. **Project design context** — read the project root's `design.md` / `DESIGN.md`
   (written by `ui-ux-pro-max --persist`) or a `## Design Context` section in
   `CLAUDE.md`. If neither exists, note that the critique is running without
   declared brand/audience context and judge on general principles.

---

Conduct a holistic design critique, evaluating whether the interface actually works — not just technically, but as a designed experience. Think like a design director giving feedback.

## Phase 1: Design Critique

Evaluate the interface across these dimensions:

### 1. AI Slop Detection (CRITICAL)

**This is the most important check.** Does this look like every other AI-generated interface from 2024-2025?

Check for the AI color palette (cyan-on-dark, purple-to-blue gradients, neon accents), gradient text, dark mode with glowing accents, decorative glassmorphism, hero metric layouts, identical card grids, and generic fonts (Inter, Roboto, Arial, Open Sans, system defaults).

**This is Hallmark's specialty, not this skill's.** For a full anti-slop punch list, run `hallmark audit <target>` — it grades against a far deeper named anti-pattern catalog with genre-aware exceptions. Flag the obvious tells here, then defer.

**The test**: If you showed this to someone and said "AI made this," would they believe you immediately? If yes, that's the problem.

### 2. Visual Hierarchy
- Does the eye flow to the most important element first?
- Is there a clear primary action? Can you spot it in 2 seconds?
- Do size, color, and position communicate importance correctly?
- Is there visual competition between elements that should have different weights?

### 3. Information Architecture & Cognitive Load
> *Consult [cognitive-load](reference/cognitive-load.md) for the working memory rule and 8-item checklist*
- Is the structure intuitive? Would a new user understand the organization?
- Is related content grouped logically?
- Are there too many choices at once? Count visible options at each decision point — if >4, flag it
- Is the navigation clear and predictable?
- **Progressive disclosure**: Is complexity revealed only when needed, or dumped on the user upfront?
- **Run the 8-item cognitive load checklist** from the reference. Report failure count: 0–1 = low (good), 2–3 = moderate, 4+ = critical.

### 4. Emotional Journey
- What emotion does this interface evoke? Is that intentional?
- Does it match the brand personality?
- Does it feel trustworthy, approachable, premium, playful — whatever it should feel?
- Would the target user feel "this is for me"?
- **Peak-end rule**: Is the most intense moment positive? Does the experience end well (confirmation, celebration, clear next step)?
- **Emotional valleys**: Check for onboarding frustration, error cliffs, feature discovery gaps, or anxiety spikes at high-stakes moments (payment, delete, commit)
- **Interventions at negative moments**: Are there design interventions where users are likely to feel frustrated or anxious? (progress indicators, reassurance copy, undo options, social proof)

### 5. Discoverability & Affordance
- Are interactive elements obviously interactive?
- Would a user know what to do without instructions?
- Are hover/focus states providing useful feedback?
- Are there hidden features that should be more visible?

### 6. Composition & Balance
- Does the layout feel balanced or uncomfortably weighted?
- Is whitespace used intentionally or just leftover?
- Is there visual rhythm in spacing and repetition?
- Does asymmetry feel designed or accidental?

### 7. Typography as Communication
- Does the type hierarchy clearly signal what to read first, second, third?
- Is body text comfortable to read? (line length, spacing, size)
- Do font choices reinforce the brand/tone?
- Is there enough contrast between heading levels?

### 8. Color with Purpose
- Is color used to communicate, not just decorate?
- Does the palette feel cohesive?
- Are accent colors drawing attention to the right things?
- Does it work for colorblind users? (not just technically — does meaning still come through?)

### 9. States & Edge Cases
- Empty states: Do they guide users toward action, or just say "nothing here"?
- Loading states: Do they reduce perceived wait time?
- Error states: Are they helpful and non-blaming?
- Success states: Do they confirm and guide next steps?

### 10. Microcopy & Voice
- Is the writing clear and concise?
- Does it sound like a human (the right human for this brand)?
- Are labels and buttons unambiguous?
- Does error copy help users fix the problem?

## Phase 2: Present Findings

Structure your feedback as a design director would:

### Design Health Score
> *Consult [heuristics-scoring](reference/heuristics-scoring.md)*

Score each of Nielsen's 10 heuristics 0–4. Present as a table:

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | ? | [specific finding or "—" if solid] |
| 2 | Match System / Real World | ? | |
| 3 | User Control and Freedom | ? | |
| 4 | Consistency and Standards | ? | |
| 5 | Error Prevention | ? | |
| 6 | Recognition Rather Than Recall | ? | |
| 7 | Flexibility and Efficiency | ? | |
| 8 | Aesthetic and Minimalist Design | ? | |
| 9 | Error Recovery | ? | |
| 10 | Help and Documentation | ? | |
| **Total** | | **??/40** | **[Rating band]** |

Be honest with scores. A 4 means genuinely excellent. Most real interfaces score 20–32.

### Anti-Patterns Verdict
**Start here.** Pass/fail: Does this look AI-generated? List specific tells from the skill's Anti-Patterns section. Be brutally honest.

### Overall Impression
A brief gut reaction — what works, what doesn't, and the single biggest opportunity.

### What's Working
Highlight 2–3 things done well. Be specific about why they work.

### Priority Issues
The 3–5 most impactful design problems, ordered by importance.

For each issue, tag with **P0–P3 severity** (consult [heuristics-scoring](reference/heuristics-scoring.md) for severity definitions):
- **[P?] What**: Name the problem clearly
- **Why it matters**: How this hurts users or undermines goals
- **Fix**: What to do about it (be concrete)
- **Suggested fix**: One concrete correction, stated as an edit — not a command name.

### Persona Red Flags
> *Consult [personas](reference/personas.md)*

Auto-select 2–3 personas most relevant to this interface type (use the selection table in the reference). If the project has a `design.md` / `DESIGN.md` or a `## Design Context` section in `CLAUDE.md`, also generate 1–2 project-specific personas from the audience/brand info.

For each selected persona, walk through the primary user action and list specific red flags found:

**Alex (Power User)**: No keyboard shortcuts detected. Form requires 8 clicks for primary action. Forced modal onboarding. ⚠️ High abandonment risk.

**Jordan (First-Timer)**: Icon-only nav in sidebar. Technical jargon in error messages ("404 Not Found"). No visible help. ⚠️ Will abandon at step 2.

Be specific — name the exact elements and interactions that fail each persona. Don't write generic persona descriptions; write what broke for them.

### Minor Observations
Quick notes on smaller issues worth addressing.

**Remember**:
- Be direct — vague feedback wastes everyone's time
- Be specific — "the submit button" not "some elements"
- Say what's wrong AND why it matters to users
- Give concrete suggestions, not just "consider exploring..."
- Prioritize ruthlessly — if everything is important, nothing is
- Don't soften criticism — developers need honest feedback to ship great design

## Phase 3: Ask the User

**After presenting findings**, use targeted questions based on what was actually found. STOP and call the AskUserQuestion tool to clarify. These answers will shape the action plan.

Ask questions along these lines (adapt to the specific findings — do NOT ask generic questions):

1. **Priority direction**: Based on the issues found, ask which category matters most to the user right now. For example: "I found problems with visual hierarchy, color usage, and information overload. Which area should we tackle first?" Offer the top 2–3 issue categories as options.

2. **Design intent**: If the critique found a tonal mismatch, ask whether it was intentional. For example: "The interface feels clinical and corporate. Is that the intended tone, or should it feel warmer/bolder/more playful?" Offer 2–3 tonal directions as options based on what would fix the issues found.

3. **Scope**: Ask how much the user wants to take on. For example: "I found N issues. Want to address everything, or focus on the top 3?" Offer scope options like "Top 3 only", "All issues", "Critical issues only".

4. **Constraints** (optional — only ask if relevant): If the findings touch many areas, ask if anything is off-limits. For example: "Should any sections stay as-is?" This prevents the plan from touching things the user considers done.

**Rules for questions**:
- Every question must reference specific findings from Phase 2 — never ask generic "who is your audience?" questions
- Keep it to 2–4 questions maximum — respect the user's time
- Offer concrete options, not open-ended prompts
- If findings are straightforward (e.g., only 1–2 clear issues), skip questions and go directly to Phase 4

## Phase 4: Recommended Actions

**After receiving the user's answers**, present a prioritized action summary reflecting the user's priorities and scope from Phase 3.

### Action Summary

List concrete fixes in priority order, based on the user's answers:

1. **[dimension] What to change** — the specific edit, with file/component if known
2. **[dimension] What to change** — …

**Rules for recommendations**:
- Order by the user's stated priorities first, then by impact
- Each item must be an actionable edit, not a vague direction ("cut the hero to one CTA and move the trust strip below the fold", not "simplify the hero")
- Map each Priority Issue to exactly one fix; drop issues the user scoped out
- If the user chose a limited scope, only include items within that scope
- If the user marked areas as off-limits, exclude fixes that would touch them

**Handoff**: this skill diagnoses, it does not edit. When the user wants the fixes applied:
- Visual/structural rework → `hallmark redesign <target>` (preserves routes, copy intent, and IA; replaces the visual layer)
- Measured a11y / performance / responsive verification → `chrome-devtools` MCP:
  `lighthouse_audit`, `performance_start_trace`, `emulate`
- Style, palette, or typography selection → `ui-ux-pro-max`

After presenting the summary, tell the user:

> You can ask me to run these one at a time, all at once, or in any order you prefer.
>
> Re-run `/critique` after fixes to see your score improve.