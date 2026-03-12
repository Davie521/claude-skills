#!/usr/bin/env python3
"""
md2html.py — Convert Markdown to styled cheatsheet HTML (A4 landscape, multi-column).

Usage:
    python3 md2html.py input.md [-o output.html]

Markdown Syntax:
    ---                     Front-matter delimiter (YAML-like, at file start)
    ---PAGE---              Page break
    # Ch0: Introduction     Chapter header (blue bar)
    ## Subsection Title     New block + red inline header
    @@Inline Title@@        Additional inline red header (same paragraph)
    **bold text**           Bold
    $formula$               Math formula (blue italic)
    $=key formula=$         Key formula (yellow bg + blue)
    ==key text==            Key text highlight (yellow bg)
    ^{superscript}          Superscript
    _{subscript}            Subscript
    ~{grey text}~           Grey/dim text
    | col1 | col2 |        Table (with |---|---| separator for headers)
    > note text             Green note box

    Blank lines separate paragraphs within a ## block.
    First paragraph after ## is joined inline with the subsection title.
"""

import re
import sys
import argparse

# ──────────────────────── CSS TEMPLATE ────────────────────────

CSS = r"""
  @page { size: A4 landscape; margin: 0; }
  @media print {
    body { background: #fff; margin: 0; padding: 0; }
    .page { box-shadow: none; margin: 0; page-break-after: always; page-break-inside: avoid; }
    .page:last-child { page-break-after: auto; }
    html, body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif;
    font-size: 6pt;
    line-height: 1.22;
    color: #222;
    background: #e5e5e5;
  }

  .page {
    width: 297mm; height: 210mm;
    padding: 3mm;
    column-count: 5;
    column-gap: 3mm;
    column-rule: 0.3px solid #bbb;
    column-fill: auto;
    overflow: hidden;
    background: #fff;
    margin: 4mm auto;
    box-shadow: 0 1px 6px rgba(0,0,0,0.2);
  }
  .s {
    background: #1a365d;
    color: #fff;
    font-size: 7pt;
    font-weight: 700;
    padding: 1.2px 4px;
    margin: 3px 0 1.5px 0;
    break-after: avoid;
    letter-spacing: 0.3px;
  }
  .s:first-child { margin-top: 0; }

  .h { color: #b91c1c; font-weight: 700; font-size: 6.2pt; }

  .m { color: #1e40af; font-family: 'Cambria Math','Times New Roman',serif; font-style: italic; font-size: 6.5pt; }

  .k { background: #fef3c7; padding: 0 1.5px; border-radius: 1px; }

  .note { background: #ecfdf5; border-left: 1.5px solid #10b981; padding: 0.5px 3px; margin: 1px 0; font-size: 5.5pt; }

  table { width: 100%; border-collapse: collapse; font-size: 5.8pt; margin: 1.5px 0; }
  th { background: #dbeafe; color: #1e40af; font-weight: 700; text-align: left; padding: 1px 2.5px; border-bottom: 0.5px solid #93c5fd; }
  td { padding: 0.8px 2.5px; border-bottom: 0.3px solid #e5e7eb; }

  b { color: #1a1a1a; }
  .g { color: #6b7280; font-size: 5.6pt; }
  sup, sub { font-size: 82%; line-height: 0; }
  p { margin: 0.8px 0; overflow-wrap: break-word; }


  .break-avoid { break-inside: avoid; }

"""

# ──────────────────────── INLINE FORMATTING ────────────────────────

def html_escape(text):
    """Escape HTML special chars in source text."""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text


def convert_inline(text):
    """Convert inline markdown formatting to HTML spans."""
    text = html_escape(text)

    # Superscript: ^{...} (supports one level of nested braces)
    text = re.sub(r'\^\{([^{}]*(?:\{[^}]*\}[^{}]*)*)\}', r'<sup>\1</sup>', text)
    # Subscript: _{...} (supports one level of nested braces)
    text = re.sub(r'_\{([^{}]*(?:\{[^}]*\}[^{}]*)*)\}', r'<sub>\1</sub>', text)
    # Key formula: $=...=$
    text = re.sub(r'\$=(.*?)=\$', r'<span class="k"><span class="m">\1</span></span>', text)
    # Regular math: $...$  (non-greedy, no nested $)
    text = re.sub(r'\$([^$]+?)\$', r'<span class="m">\1</span>', text)
    # Key text: ==...==
    text = re.sub(r'==(.*?)==', r'<span class="k">\1</span>', text)
    # Bold: **...**
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Inline subsection header: @@...@@
    text = re.sub(r'@@(.*?)@@', r'<span class="h">\1</span>', text)
    # Grey text: ~{...}~
    text = re.sub(r'~\{([^}]*)\}~', r'<span class="g">\1</span>', text)

    return text

# ──────────────────────── TABLE RENDERING ────────────────────────

def render_table(lines):
    """Convert markdown table lines to HTML <table>."""
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        rows.append(cells)

    # Detect header separator row (all dashes/colons)
    has_header = (len(rows) > 1 and
                  all(re.match(r'^:?-+:?$', c.strip()) for c in rows[1]))

    html = '<table>\n'
    if has_header:
        html += '<tr>' + ''.join(f'<th>{convert_inline(c)}</th>' for c in rows[0]) + '</tr>\n'
        data_rows = rows[2:]
    else:
        data_rows = rows

    for row in data_rows:
        html += '<tr>' + ''.join(f'<td>{convert_inline(c)}</td>' for c in row) + '</tr>\n'
    html += '</table>\n'
    return html

# ──────────────────────── FRONT MATTER ────────────────────────

def parse_front_matter(text):
    """Extract YAML-like front matter from markdown text."""
    meta = {}
    content = text

    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
    if m:
        for line in m.group(1).strip().split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                meta[key.strip()] = val.strip().strip('"').strip("'")
        content = text[m.end():]

    return meta, content

# ──────────────────────── BLOCK PARSER ────────────────────────

def flush_block(blocks, block):
    """Close current block and add to blocks list."""
    if block is None:
        return
    # Flush any buffered lines as a paragraph
    if block.get('_lines'):
        block['items'].append(('para', list(block['_lines'])))
        block['_lines'] = []
    blocks.append(block)


def parse_blocks(text):
    """Parse page text into a list of block dicts."""
    lines = text.split('\n')
    blocks = []
    cur = None  # current block being built
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # ── Chapter header: # Title ──
        if re.match(r'^#\s+', stripped) and not stripped.startswith('## '):
            flush_block(blocks, cur)
            cur = None
            title = re.sub(r'^#\s+', '', stripped)
            blocks.append({'type': 'section', 'title': title})

        # ── Subsection header: ## Title ──
        elif stripped.startswith('## '):
            flush_block(blocks, cur)
            title = stripped[3:].strip()
            cur = {'type': 'subsection', 'title': title, 'items': [], '_lines': []}

        # ── Table row: | ... | ──
        elif stripped.startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].strip())
                i += 1
            i -= 1  # will be incremented at end of loop

            if cur is not None:
                # Table inside current block
                if cur['_lines']:
                    cur['items'].append(('para', list(cur['_lines'])))
                    cur['_lines'] = []
                cur['items'].append(('table', table_lines))
            else:
                # Standalone table
                blocks.append({'type': 'table', 'lines': table_lines})

        # ── Note: > text ──
        elif stripped.startswith('> '):
            # Accumulate consecutive > lines
            note_lines = []
            while i < len(lines) and lines[i].strip().startswith('> '):
                note_lines.append(lines[i].strip()[2:])
                i += 1
            i -= 1
            flush_block(blocks, cur)
            cur = None
            blocks.append({'type': 'note', 'text': ' '.join(note_lines)})

        # ── Blank line ──
        elif stripped == '':
            if cur is not None and cur['_lines']:
                cur['items'].append(('para', list(cur['_lines'])))
                cur['_lines'] = []

        # ── Regular text ──
        else:
            if cur is None:
                cur = {'type': 'subsection', 'title': None, 'items': [], '_lines': []}
            cur['_lines'].append(stripped)

        i += 1

    flush_block(blocks, cur)
    return blocks

# ──────────────────────── HTML RENDERING ────────────────────────

def render_blocks(blocks):
    """Render parsed blocks to HTML string."""
    parts = []
    for block in blocks:
        btype = block['type']

        if btype == 'section':
            parts.append(f'<div class="s">{convert_inline(block["title"])}</div>\n')

        elif btype == 'subsection':
            parts.append(render_subsection(block))

        elif btype == 'table':
            parts.append(f'<div class="break-avoid">\n{render_table(block["lines"])}</div>\n')

        elif btype == 'note':
            parts.append(
                f'<div class="break-avoid">\n'
                f'<div class="note">{convert_inline(block["text"])}</div>\n'
                f'</div>\n'
            )

    return '\n'.join(parts)


def render_subsection(block):
    """Render a subsection block (with optional title) to HTML."""
    # Use break-avoid for all titled subsection blocks
    use_break_avoid = bool(block.get('title'))
    if use_break_avoid:
        html = '<div class="break-avoid">\n'
    else:
        html = ''
    first_para = True

    for item_type, item_data in block['items']:
        if item_type == 'para':
            text = ' '.join(item_data)
            text = convert_inline(text)
            if first_para and block.get('title'):
                html += f'<p><span class="h">{convert_inline(block["title"])}</span> {text}</p>\n'
                first_para = False
            else:
                html += f'<p>{text}</p>\n'
                first_para = False
        elif item_type == 'table':
            if first_para and block.get('title'):
                # Title before table with no preceding text
                html += f'<p><span class="h">{convert_inline(block["title"])}</span></p>\n'
                first_para = False
            html += render_table(item_data)

    # Handle title-only block (no content)
    if first_para and block.get('title'):
        html += f'<p><span class="h">{convert_inline(block["title"])}</span></p>\n'

    if use_break_avoid:
        html += '</div>\n'
    return html

# ──────────────────────── MAIN CONVERSION ────────────────────────

def convert(md_text):
    """Convert full markdown text to complete HTML document."""
    meta, content = parse_front_matter(md_text)
    title = meta.get('title', 'Cheat Sheet')
    subtitle = meta.get('subtitle', '')

    # Split into pages
    page_texts = re.split(r'^---\s*PAGE\s*---\s*$', content, flags=re.MULTILINE)

    html_pages = []
    for idx, page_text in enumerate(page_texts):
        page_text = page_text.strip()
        if not page_text:
            continue

        blocks = parse_blocks(page_text)

        # Collect chapter titles for page subtitle
        chapter_titles = [b['title'] for b in blocks if b['type'] == 'section']

        body = render_blocks(blocks)
        html_pages.append(f'<div class="page">\n\n{body}\n</div>')

    # Assemble full document
    doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{html_escape(title)}</title>
<style>{CSS}</style>
</head>
<body>

{''.join(html_pages)}

</body>
</html>
'''
    return doc


def main():
    parser = argparse.ArgumentParser(description='Convert Markdown to cheatsheet HTML')
    parser.add_argument('input', help='Input markdown file')
    parser.add_argument('-o', '--output', help='Output HTML file (default: stdout)')
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        md_text = f.read()

    html = convert(md_text)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'Written to {args.output}')
    else:
        print(html)


if __name__ == '__main__':
    main()
