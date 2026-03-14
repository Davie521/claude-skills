---
name: cheatsheet
description: Create dense, printable A4 landscape cheatsheets from Markdown using a custom syntax with multi-column layout. Use when the user asks to create a cheatsheet, revision sheet, crib sheet, or condensed reference document for exams, courses, or technical topics. Supports math formulas, tables, highlights, notes, and multi-page output. Converts Markdown to styled HTML and exports to PDF for printing.
---

# Cheatsheet Creator

Create dense, printable A4 landscape cheatsheets (297mm x 210mm, 5 columns, 6pt font) from a custom Markdown dialect.

## Pipeline

```
Content → Write .md (custom syntax) → Run md2html.py → .html → Export PDF → Print
```

## Quick Start

1. Create a `.md` file with front matter and content (see Syntax below)
2. Convert: `python3 scripts/md2html.py input.md -o output.html`
3. Export PDF: open HTML in browser → Ctrl+P → A4 Landscape, No margins, Background graphics ON → Save as PDF

## Markdown Syntax

For complete syntax details, see [references/cheatsheet_spec.md](references/cheatsheet_spec.md).

### Block Elements

| Syntax | Result |
|--------|--------|
| `# Title` | Blue section header banner |
| `## Title` | Red inline subsection header (first paragraph joins inline) |
| `---PAGE---` | Page break (new A4 page) |
| `> text` | Green note box |
| `\| a \| b \|` | Table (with `\|---\|` separator = blue header) |
| Blank line | Paragraph separator |

### Inline Elements

| Syntax | Result |
|--------|--------|
| `**bold**` | **Bold** |
| `$formula$` | Blue italic math |
| `$=key formula=$` | Yellow-highlighted math |
| `==key text==` | Yellow highlight |
| `@@inline title@@` | Red inline header (no break-avoid) |
| `^{text}` | Superscript |
| `_{text}` | Subscript |
| `~{text}~` | Grey small text |

### Document Structure

```markdown
---
title: My Cheat Sheet
subtitle:
---

# Section Title

## Subsection
First paragraph joins inline with title. $formula$ and **bold**.

Second paragraph is separate. ==highlight==.

## Another Subsection
| Col1 | Col2 |
|------|------|
| data | data |

> Important note

---PAGE---

# Page 2 Section
...
```

## Layout Rules

- **Page**: A4 landscape (297mm x 210mm), 5 columns, 3mm gaps, 3mm padding
- **Font**: 6pt base, line-height 1.22
- **Column fill**: `auto` — left-to-right, top-to-bottom
- **Overflow**: `hidden` — content beyond page boundary is **silently lost**
- **Break-avoid**: Every `##` block stays intact (won't split across columns), causing small gaps at column bottoms

### Capacity Planning

- Each page holds ~370-400 source lines of rendered content
- Target: fill all 5 columns per page (last column can be slightly short)
- Use `wc -l` to track line count during editing

### Content Density Tips

- Use Unicode symbols: `→ ≈ ∈ ⊙ Σ Π ∂ ≤ ≥ ² ³`
- Use abbreviations and shorthand
- Keep `##` blocks small (1-3 paragraphs) to minimize column-bottom gaps
- Split large blocks into multiple `##` sections
- Tables: keep under 8 rows
- Use `@@sub-title@@` for sub-headers within a `##` block (avoids creating new break-avoid)

### Multi-Page Workflow — Page-by-Page

Work one page at a time. Do NOT write all pages at once.

1. **Page 1**: Write ~380 lines of content (no `---PAGE---` yet)
2. Run `md2html.py` → open HTML → verify all 5 columns are filled
3. If under-filled: add more content. If overflowing: trim or move content to next page
4. Once Page 1 is good, append `---PAGE---` and start **Page 2** content
5. Repeat: write → build → verify → adjust for each page
6. Continue until all content is placed

> **Why page-by-page?** Writing everything at once makes it hard to judge density. Tables and `##` break-avoid blocks consume unpredictable vertical space. Filling one page at a time ensures every page uses all 5 columns with no overflow.

## HTML Generation

The converter script (`scripts/md2html.py`) is zero-dependency Python:

```bash
python3 scripts/md2html.py input.md -o output.html
```

Open `output.html` in a browser to preview. The CSS renders the exact print layout on screen.

## PDF Export

### Method 1: Browser Print (Recommended)

Open HTML in Chrome/Safari → Ctrl+P (Cmd+P on Mac):
- Layout: **Landscape**
- Paper: **A4**
- Margins: **None**
- Background graphics: **ON**
- Save as PDF

### Method 2: Playwright Screenshot-to-PDF

When browser print is unavailable, use Playwright to capture high-resolution screenshots and convert to PDF with Pillow. This bypasses CSS print pagination issues.

```python
# 1. Start HTTP server in the directory with the HTML file
# python3 -m http.server 8765

# 2. Playwright: capture each .page element at 4x scale
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(
        viewport={"width": 1122, "height": 794},
        device_scale_factor=4
    )
    page = ctx.new_page()
    page.goto("http://localhost:8765/output.html")
    page.wait_for_load_state("networkidle")

    pages_el = page.locator(".page")
    for i in range(pages_el.count()):
        pages_el.nth(i).screenshot(path=f"page{i+1}.png")

    browser.close()

# 3. Convert to PDF with Pillow
from PIL import Image

A4_W, A4_H = 3508, 2480  # 300 DPI A4 landscape
images = []
for i in range(num_pages):
    img = Image.open(f"page{i+1}.png")
    img = img.resize((A4_W, A4_H), Image.LANCZOS).convert("RGB")
    images.append(img)

images[0].save(
    "output.pdf", "PDF", resolution=300.0,
    save_all=True, append_images=images[1:]
)
```

**Do NOT use** Chrome headless `--print-to-pdf` or Playwright `page.pdf()` — these fail to render multi-page `.page` divs correctly (second page renders blank).

## Gotchas

| Issue | Solution |
|-------|----------|
| Content invisible / cut off | `overflow: hidden` — reduce content or add `---PAGE---` |
| Large column-bottom gaps | Break `##` blocks into smaller ones (1-3 paragraphs) |
| Table overflows column | Shorten cell text, remove backtick formatting, abbreviate |
| `\|` in formulas parsed as table | Use `‖` or `·` instead of `\|` inside table cells |
| Second PDF page blank | Use screenshot-to-PDF method, NOT Chrome print-to-pdf |
| Content not enough / right columns empty | Add more content to fill ~380 lines per page |

## Verification Checklist

After generating HTML, verify:

1. **No overflow**: `scrollHeight ≈ clientHeight` for each `.page` div (check via browser DevTools)
2. **All columns filled**: visually confirm 5 columns on each page have content
3. **No table overflow**: no text bleeding into adjacent columns
4. **Highlights render**: yellow `==` and `$= =$` backgrounds visible
5. **Page count correct**: exact number of intended pages
