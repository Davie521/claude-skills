---
name: llm-cost-discipline
description: Cost discipline for LLM pipelines — parse structured text with regex first and escalate only flagged items to an LLM, route the cheapest sufficient model tier by task size, track budget, retry narrowly, cache prompts. Use when building LLM pipelines, controlling API costs, or choosing between regex and LLM for parsing structured text (构建 LLM 管道、控制 API 成本、解析结构化文本选方案时).
origin: ECC
---

# LLM Cost Discipline

Two layers of cost control, applied in order:

1. **Avoid the call** — for structured text with repeating patterns, regex handles 95-98% of items deterministically; only flagged edge cases reach an LLM.
2. **Cheapen the call** — when you must call, route the cheapest sufficient model tier by task size, cache the stable prompt prefix, track spend against a budget, and retry only transient errors.

## When to Activate

- Parsing structured text (quizzes, forms, invoices, tables) and deciding regex vs LLM
- Building batch pipelines where API spend adds up
- Need budget guardrails or model routing in production

## Layer 1: Regex First, LLM for Flagged Items Only

```
Is the text format consistent and repeating?
├── Yes (>90% follows a pattern) → Start with regex
│   ├── Regex handles 95%+ → Done, no LLM needed
│   └── Regex handles <95% → LLM for flagged items only
└── No (free-form, highly variable) → Use LLM directly
```

Pipeline: regex parse → score confidence → escalate only flagged items to the cheap-tier model.

### Regex parser

```python
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class ParsedItem:
    id: str
    text: str
    choices: tuple[str, ...]
    answer: str

def parse_structured_text(content: str) -> list[ParsedItem]:
    pattern = re.compile(
        r"(?P<id>\d+)\.\s*(?P<text>.+?)\n"
        r"(?P<choices>(?:[A-D]\..+?\n)+)"
        r"Answer:\s*(?P<answer>[A-D])",
        re.MULTILINE | re.DOTALL,
    )
    return [
        ParsedItem(m.group("id"), m.group("text").strip(),
                   tuple(c.strip() for c in re.findall(r"[A-D]\.\s*(.+)", m.group("choices"))),
                   m.group("answer"))
        for m in pattern.finditer(content)
    ]
```

### Confidence scoring — escalate on reasons, rank by score

Do NOT gate escalation on a magic threshold like `score < 0.95`. With deductions of 0.2/0.3/0.5 the score is either exactly 1.0 (clean) or ≤ 0.8 (flagged), so any threshold in (0.8, 1.0) is dead code dressed up as precision. The real decision is binary — "did we detect an issue?" — and the score's job is to rank flagged items by severity when the LLM budget caps how many you can fix.

```python
@dataclass(frozen=True)
class ConfidenceFlag:
    item_id: str
    score: float                # severity rank: 1.0 clean, lower = worse
    reasons: tuple[str, ...]

_DEDUCTIONS = {"few_choices": 0.3, "missing_answer": 0.5, "short_text": 0.2}

def score_confidence(item: ParsedItem) -> ConfidenceFlag:
    checks = {"few_choices": len(item.choices) < 3,
              "missing_answer": not item.answer,
              "short_text": len(item.text) < 10}
    reasons = tuple(r for r, bad in checks.items() if bad)
    score = max(0.0, 1.0 - sum(_DEDUCTIONS[r] for r in reasons))
    return ConfidenceFlag(item.id, score, reasons)

def identify_low_confidence(items: list[ParsedItem]) -> list[ConfidenceFlag]:
    """Any detected issue escalates; worst items first."""
    flags = (score_confidence(i) for i in items)
    return sorted((f for f in flags if f.reasons), key=lambda f: f.score)
```

### LLM validator (flagged items only)

Parse the LLM reply and fall back to the regex output on failure — never crash the pipeline on a malformed model response, and never return a variable no branch assigned.

```python
import dataclasses, json

MODEL_CHEAP = "claude-haiku-4-5"    # cheap tier — verify current ids via the claude-api skill
MODEL_STRONG = "claude-sonnet-4-6"  # strong tier

def validate_with_llm(item: ParsedItem, original_text: str, client) -> ParsedItem:
    response = client.messages.create(
        model=MODEL_CHEAP,  # cheapest tier is sufficient for validation
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": (
                f"Extract the question, choices, and answer from this text.\n\n"
                f"Text: {original_text}\n\nCurrent extraction: {item}\n\n"
                'Reply CORRECT if accurate, else corrected JSON only: '
                '{"text": ..., "choices": [...], "answer": ...}'
            ),
        }],
    )
    raw = response.content[0].text.strip()
    if raw == "CORRECT":
        return item
    try:
        data = json.loads(raw)
        return dataclasses.replace(
            item, text=data["text"], choices=tuple(data["choices"]), answer=data["answer"],
        )
    except (json.JSONDecodeError, KeyError, TypeError):
        return item  # keep the regex output; log for review
```

Wire-up: `parse_structured_text` → `identify_low_confidence` → rebuild the list, passing only flagged ids through `validate_with_llm` (no client provided → return the regex output as-is).

## Layer 2: Route the Cheapest Sufficient Model

When a call is unavoidable, pick the tier by task size:

| Signal | Route to |
|---|---|
| text < 10K chars AND items < 30 | Cheap tier (Haiku-class) |
| text ≥ 10K chars OR items ≥ 30 | Strong tier (Sonnet-class) |
| Caller forces a model | The forced model |

```python
def select_model(text_length: int, item_count: int, force_model: str | None = None) -> str:
    if force_model is not None:
        return force_model
    if text_length >= 10_000 or item_count >= 30:
        return MODEL_STRONG
    return MODEL_CHEAP
```

Log routing decisions and tune the thresholds from real quality data.

### Budget tracking (immutable)

```python
@dataclass(frozen=True, slots=True)
class CostRecord:
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float   # compute from response.usage × current per-token prices

@dataclass(frozen=True, slots=True)
class CostTracker:
    budget_limit: float = 1.00
    records: tuple[CostRecord, ...] = ()

    def add(self, record: CostRecord) -> "CostTracker":
        return CostTracker(self.budget_limit, (*self.records, record))

    @property
    def total_cost(self) -> float:
        return sum(r.cost_usd for r in self.records)

    @property
    def over_budget(self) -> bool:
        return self.total_cost > self.budget_limit
```

Check `over_budget` before each call and fail early rather than overspend. Never mutate tracking state — immutable records make audits trivial.

### Retry and prompt caching

- **Retry**: the Anthropic SDK already retries transient failures (connection errors, 429, 5xx) with exponential backoff — set `max_retries` on the client instead of hand-rolling a loop. Never retry auth or validation errors: they are permanent and only burn budget.
- **Prompt caching**: cache system prompts over ~1024 tokens with `cache_control: {"type": "ephemeral"}` on the stable prefix — saves cost and latency on every repeat call.

## Pricing: Look It Up, Never Hardcode

Do not maintain a model pricing table in code or docs — it goes stale. Resolve current model ids and per-token prices from the global claude-api skill or the official Anthropic pricing page, and compute `cost_usd` at runtime from `response.usage` token counts.

## Evidence: 410-Item Production Quiz-Parsing Run

| Metric | Value |
|--------|-------|
| Regex success rate | 98.0% |
| Flagged (low-confidence) items | 8 (2.0%) |
| LLM calls needed | ~5 |
| Cost savings vs all-LLM | ~95% |
| Test coverage | 93% |

## Anti-Patterns

- Sending all text to an LLM when regex handles 95%+ (expensive and slow)
- Using regex for free-form, highly variable text (LLM is better there)
- Confidence thresholds the scoring function can never land between (see confidence scoring above)
- Using the most expensive model regardless of task size; retrying permanent errors
- Mutating parsed items or cost state; hardcoding model prices inline
