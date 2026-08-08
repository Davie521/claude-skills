---
name: skill-comply
description: Visualize whether skills, rules, and agent definitions are actually followed — auto-generates scenarios at 3 prompt strictness levels, runs agents, classifies behavioral sequences, and reports compliance rates with full tool call timelines
origin: ECC
tools: Read, Bash
---

# skill-comply: Automated Compliance Measurement

Measures whether coding agents actually follow skills, rules, or agent definitions by:
1. Auto-generating expected behavioral sequences (specs) from any .md file
2. Auto-generating scenarios with decreasing prompt strictness (supportive → neutral → competing)
3. Running `claude -p` and capturing tool call traces via stream-json
4. Classifying tool calls against spec steps using LLM (not regex)
5. Checking temporal ordering deterministically
6. Generating self-contained reports with spec, prompts, and timelines

## Supported Targets

- **Skills** (`plugins/*/skills/*/SKILL.md`): Workflow skills like search-routing, tdd-workflow
- **Rules** (only if you maintain a `~/.claude/rules/` directory — none exists by default): mandatory rules like testing.md, security.md, git-workflow.md
- **Agent definitions** (`agents/*.md`): Whether an agent gets invoked when expected (internal workflow verification not yet supported)

## When to Activate

- User runs `/skill-comply <path>`
- User asks "is this rule actually being followed?"
- After adding new rules/skills, to verify agent compliance
- Periodically as part of quality maintenance

## Usage

Run from this skill's directory (where `pyproject.toml` lives):

```bash
cd "${CLAUDE_PLUGIN_ROOT}/skills/skill-comply"

# Full run (target: any skill/rule .md — here a real skill from this marketplace repo)
uv run python -m scripts.run "${CLAUDE_PLUGIN_ROOT}/../quality/skills/tdd-workflow/SKILL.md"

# Dry run (no cost, spec + scenarios only)
uv run python -m scripts.run --dry-run "${CLAUDE_PLUGIN_ROOT}/../research/skills/search-routing/SKILL.md"

# Rules work the same way, if you maintain a rules directory
# (e.g. uv run python -m scripts.run ~/.claude/rules/common/testing.md)

# Custom models
uv run python -m scripts.run --gen-model haiku --model sonnet <path>
```

## Key Concept: Prompt Independence

Measures whether a skill/rule is followed even when the prompt doesn't explicitly support it.

## Report Contents

Reports are self-contained and include:
1. Expected behavioral sequence (auto-generated spec)
2. Scenario prompts (what was asked at each strictness level)
3. Compliance scores per scenario
4. Tool call timelines with LLM classification labels

### Advanced (optional)

For users familiar with hooks, reports also include hook promotion recommendations for steps with low compliance. This is informational — the main value is the compliance visibility itself.
