#!/usr/bin/env python3
"""Generate the license files that ship with every plugin.

A plugin is installed from its own directory (plugins/<name>), so the root
LICENSE and THIRD_PARTY_NOTICES.md never reach the user's machine. This script
writes, from the SOURCES table below:

  THIRD_PARTY_NOTICES.md                    every third-party source in the repo
  plugins/<name>/LICENSE                    copy of the root LICENSE
  plugins/<name>/THIRD_PARTY_NOTICES.md     only the sources that plugin contains

A plugin that is entirely another author's work (a source with
"whole_plugin": True) keeps that author's LICENSE; no copy is written over it.

Usage:
  python3 tools/license_notices.py          write the files, delete stale notices
  python3 tools/license_notices.py --check  exit 1 if any file is out of date or
                                            stale, or a listed path is missing

When you migrate or graft material from another project, add it to SOURCES
and run the script.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTICES = "THIRD_PARTY_NOTICES.md"

# Each source:
#   name, url, license, copyright, note
#   license_text   file under licenses/ reproduced in full in the notices
#   extra_texts    further files reproduced in full (e.g. an Apache NOTICE)
#   license_file   license file that already sits next to the material
#   license_text_note  used when neither of the above exists
#   whole_plugin   True if the source's single path is a whole plugin that is
#                  entirely this author's work
#   paths          repo paths holding the material; an entry may be
#                  (path, "which part of it") when only part of it is borrowed
SOURCES = [
    {
        "name": "everything-claude-code",
        "url": "https://github.com/affaan-m/everything-claude-code",
        "license": "MIT",
        "copyright": "Copyright (c) 2026 Affaan Mustafa",
        "license_text": "licenses/everything-claude-code.MIT.txt",
        "note": "Copied and modified. Some of these skills credit their own "
        "authors in an `origin:` field (for example santa-method, Ronald "
        "Skelton); they reached this repository through everything-claude-code "
        "under its MIT license.",
        "paths": [
            ("plugins/business/skills/investor-materials", "including the outreach cadence merged from investor-outreach"),
            ("plugins/code-review/agents", "the five reviewer agents; swift-reviewer was written here from everything-claude-code's Swift rules"),
            ("plugins/code-review/commands/code-review.md", "the dispatcher's base; the Gate A/B triage workflow is original"),
            "plugins/data/skills/data-scraper-agent",
            "plugins/data/skills/database-migrations",
            ("plugins/dev-workflow/skills/cleanup", "Phase 4 placement rules, from the learn-eval skill"),
            ("plugins/dev-workflow/skills/deep-plan", "the plan flow it extends"),
            ("plugins/dev-workflow/skills/grill-with-docs/ADR-FORMAT.md", "the ADR spec: Index, Consent, Reading ADRs back"),
            "plugins/document/skills/visa-doc-translate",
            "plugins/quality/skills/ai-regression-testing",
            "plugins/quality/skills/click-path-audit",
            "plugins/quality/skills/e2e-testing",
            "plugins/quality/skills/plankton-code-quality",
            "plugins/quality/skills/santa-method",
            "plugins/quality/skills/security-checklist",
            "plugins/quality/skills/security-scan",
            "plugins/quality/skills/tdd-workflow",
            "plugins/research/skills/llm-cost-discipline",
            ("plugins/research/skills/research", "including the scenario checklists merged from market-research"),
            "plugins/research/skills/search-routing",
            "plugins/skills/skills/rules-distill",
            "plugins/skills/skills/skill-comply",
            "plugins/skills/skills/skill-stocktake",
            "plugins/swift/skills/foundation-models-on-device",
            "plugins/swift/skills/liquid-glass-design",
            "plugins/swift/skills/swift-concurrency-6-2",
            ("plugins/swift/skills/swiftui-patterns", "including actor-persistence and protocol-di"),
            "plugins/web/skills/api-design",
            "plugins/web/skills/bun-runtime",
            "plugins/web/skills/content-hash-cache-pattern",
            "plugins/web/skills/deployment-patterns",
            "plugins/web/skills/docker-patterns",
            "plugins/web/skills/mcp-server-patterns",
            ("plugins/writing/skills/crosspost", "including content-engine"),
            "plugins/writing/skills/video-editing",
            ("plugins/writing/skills/vibe-writing", "the voice checklist and banned-word list, from article-writing; see its Provenance footer"),
        ],
    },
    {
        "name": "supabase/agent-skills",
        "url": "https://github.com/supabase/agent-skills",
        "license": "MIT",
        "copyright": "Copyright (c) 2026 Supabase",
        "license_text": "licenses/supabase-agent-skills.MIT.txt",
        "note": "Reached this repository through everything-claude-code; the "
        "skill credits it in place.",
        "paths": [("plugins/data/skills/database-migrations", "the PostgreSQL appendix")],
    },
    {
        "name": "mattpocock/skills",
        "url": "https://github.com/mattpocock/skills",
        "license": "MIT",
        "copyright": "Copyright (c) 2026 Matt Pocock",
        "license_text": "licenses/mattpocock-skills.MIT.txt",
        "note": "Copied and modified; each skill names its upstream path in an "
        "Origin or Provenance footer.",
        "paths": [
            "plugins/dev-workflow/skills/caveman",
            "plugins/dev-workflow/skills/diagnose",
            "plugins/dev-workflow/skills/grill-with-docs",
            "plugins/dev-workflow/skills/improve-codebase-architecture",
            "plugins/dev-workflow/skills/prototype",
            "plugins/dev-workflow/skills/to-prd",
            "plugins/dev-workflow/skills/triage",
            ("plugins/quality/skills/tdd-workflow", "the grafted section named in its Provenance footer"),
        ],
    },
    {
        "name": "JuliusBrussee/caveman",
        "url": "https://github.com/JuliusBrussee/caveman",
        "license": "MIT (at commit d84127c; the project has since moved to Apache-2.0)",
        "copyright": "Copyright (c) 2026 Julius Brussee",
        "license_text": "licenses/caveman.MIT.txt",
        "note": "The original that mattpocock/skills' caveman builds on.",
        "paths": ["plugins/dev-workflow/skills/caveman"],
    },
    {
        "name": "close-skill",
        "url": "https://github.com/fogarasy/close-skill",
        "license": "MIT",
        "copyright": "Copyright (c) 2026 @thomasfogarasy",
        "license_text": "licenses/close-skill.MIT.txt",
        "note": "Checks rewritten into cleanup; see its Provenance footer.",
        "paths": ["plugins/dev-workflow/skills/cleanup"],
    },
    {
        "name": "claude-code-shepherd",
        "url": "https://github.com/mgorkemuz/claude-code-shepherd",
        "license": "MIT",
        "copyright": "Copyright (c) 2026 claude-clean contributors",
        "license_text": "licenses/claude-code-shepherd.MIT.txt",
        "note": "Ideas adapted into cleanup; see its Provenance footer.",
        "paths": ["plugins/dev-workflow/skills/cleanup"],
    },
    {
        "name": "AgentDeck",
        "url": "https://github.com/puritysb/AgentDeck",
        "license": "MIT",
        "copyright": "Copyright (c) 2025 SerendipityBound",
        "license_text": "licenses/AgentDeck.MIT.txt",
        "note": "Ideas from its session-end skill adapted into cleanup; see its "
        "Provenance footer.",
        "paths": ["plugins/dev-workflow/skills/cleanup"],
    },
    {
        "name": "openai/codex-plugin-cc",
        "url": "https://github.com/openai/codex-plugin-cc",
        "license": "Apache-2.0",
        "copyright": "Copyright 2026 OpenAI",
        "license_text": "licenses/codex-plugin-cc.Apache-2.0.txt",
        "extra_texts": ["licenses/codex-plugin-cc.NOTICE.txt"],
        "note": "Rules adapted from its codex-result-handling skill; see the "
        "skill's Provenance footer. Its NOTICE file is reproduced below.",
        "paths": [("plugins/codex/skills/codex-review", "the presentation rules under \"After the call\"")],
    },
    {
        "name": "ui-ux-pro-max-skill",
        "url": "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill",
        "license": "MIT",
        "copyright": "Copyright (c) 2024 Next Level Builder",
        "license_file": "plugins/design/skills/ui-ux-pro-max/LICENSE",
        "note": "Copied and modified.",
        "paths": ["plugins/design/skills/ui-ux-pro-max"],
    },
    {
        "name": "vercel-labs/web-interface-guidelines",
        "url": "https://github.com/vercel-labs/web-interface-guidelines",
        "license": "MIT",
        "copyright": "Copyright (c) 2025 Vercel Labs",
        "license_text": "licenses/web-interface-guidelines.MIT.txt",
        "note": "Reached this repository through ui-ux-pro-max-skill, which "
        "imported it in its commit bf0b627.",
        "paths": ["plugins/design/skills/ui-ux-pro-max/data/web-interface.csv"],
    },
    {
        "name": "vercel-labs/agent-skills (react-best-practices)",
        "url": "https://github.com/vercel-labs/agent-skills",
        "license": "MIT",
        "copyright": "Vercel",
        "license_text_note": "the repository publishes no license file; its "
        "README and the skill's metadata state MIT",
        "note": "Reached this repository through ui-ux-pro-max-skill, which "
        "imported it in its commit bf0b627.",
        "paths": ["plugins/design/skills/ui-ux-pro-max/data/react-performance.csv"],
    },
    {
        "name": "Leonxlnx/taste-skill",
        "url": "https://github.com/Leonxlnx/taste-skill",
        "license": "MIT",
        "copyright": "Copyright (c) 2026 Leonxlnx",
        "license_text": "licenses/taste-skill.MIT.txt",
        "note": "Its design-system map (section 2) was kept when the skill was "
        "retired; the file says so in a footnote.",
        "paths": ["plugins/design/skills/ui-ux-pro-max/reference/design-system-map.md"],
    },
    {
        "name": "impeccable",
        "url": "https://github.com/pbakaus/impeccable",
        "license": "Apache-2.0",
        "copyright": "Copyright 2025 Paul Bakaus",
        "license_file": "plugins/design/skills/critique/LICENSE.txt",
        "note": "Modified; the changes are listed in the skill's Origin section.",
        "paths": ["plugins/design/skills/critique"],
    },
    {
        "name": "anthropics/skills (pdf)",
        "url": "https://github.com/anthropics/skills",
        "license": "Apache-2.0 (from commit 2c5958e)",
        "copyright": "Copyright Anthropic, PBC",
        "license_file": "plugins/document/skills/pdf/LICENSE.txt",
        "note": "Modified; the changes are listed in the skill's Origin section.",
        "paths": ["plugins/document/skills/pdf"],
    },
    {
        "name": "anthropics/skills (doc-coauthoring)",
        "url": "https://github.com/anthropics/skills",
        "license": "unconfirmed",
        "copyright": "Copyright Anthropic, PBC",
        "license_text_note": "none; unlike the repository's other skills this "
        "one ships no LICENSE.txt, and the README does not name it",
        "note": "Modified. This collection's LICENSE does not cover it.",
        "paths": ["plugins/document/skills/doc-coauthoring"],
    },
    {
        "name": "codebase-to-course",
        "url": "https://github.com/zarazhangrui/codebase-to-course",
        "license": "none published",
        "copyright": "all rights reserved by the author (Zara Zhang)",
        "license_text_note": "none",
        "note": "Adapted with changes. The author has published no license "
        "(see https://github.com/zarazhangrui/codebase-to-course/issues/10), "
        "so neither this collection's LICENSE nor any open-source grant "
        "covers it. It will be removed or relicensed if the author asks or "
        "publishes terms.",
        "paths": ["plugins/document/skills/codebase-to-course"],
    },
    {
        "name": "writing-dna-skill",
        "url": "https://github.com/larashero3-dotcom/writing-dna-skill",
        "license": "MIT (at commit 9e780d0)",
        "copyright": "Copyright (c) 2026",
        "license_text": "licenses/writing-dna-skill.MIT.txt",
        "note": "Short README passages quoted for commentary, taken from the "
        "MIT-licensed revision.",
        "paths": [("plugins/document/skills/readme/references/examples.md", "quoted passages")],
    },
    {
        "name": "SoftwareCopyright-Skill",
        "url": "https://github.com/Fokkyp/SoftwareCopyright-Skill",
        "license": "MIT (at commit e78f746)",
        "copyright": "Copyright (c) 2026 Software Copyright Materials contributors",
        "license_text": "licenses/SoftwareCopyright-Skill.MIT.txt",
        "note": "Short README passages quoted for commentary, taken from the "
        "MIT-licensed revision.",
        "paths": [("plugins/document/skills/readme/references/examples.md", "quoted passages")],
    },
    {
        "name": "FlorianBruniaux/claude-code-plugins",
        "url": "https://github.com/FlorianBruniaux/claude-code-plugins",
        "license": "MIT",
        "copyright": "Copyright (c) 2026 Florian Bruniaux",
        "license_file": "plugins/session-summary/LICENSE",
        "whole_plugin": True,
        "note": "Vendored at 23883a1.",
        "paths": ["plugins/session-summary"],
    },
]

HEADER = """# Third-party notices

The Licensor's own work in {where} is licensed under the terms in `LICENSE`
(MIT with the Commons Clause). The material below comes from other authors and
stays under its original terms; neither the Licensor's LICENSE nor the Commons
Clause applies to it.
"""

HEADER_WHOLE_PLUGIN = """# Third-party notices

This plugin is another author's work, redistributed under its original license
(`LICENSE` in this directory). The Licensor's MIT-with-Commons-Clause terms do
not apply to it.
"""


def split(entry):
    return entry if isinstance(entry, tuple) else (entry, None)


def under(path, base):
    return base is None or path == base or path.startswith(base + "/")


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def render(sources, base, header):
    out = [header]
    texts = []
    for s in sources:
        out.append(f"## {s['name']}\n")
        out.append(f"- Source: {s['url']}")
        out.append(f"- License: {s['license']}; {s['copyright']}")
        if "license_file" in s:
            out.append(f"- License text: `{os.path.relpath(s['license_file'], base or '.')}`")
        elif "license_text" in s:
            out.append("- License text: reproduced at the end of this file")
        else:
            out.append(f"- License text: {s['license_text_note']}")
        out.append(f"- {s['note']}")
        out.append("- Paths:")
        for entry in s["paths"]:
            path, part = split(entry)
            if not under(path, base):
                continue
            shown = os.path.relpath(path, base) if base else path
            out.append(f"  - `{shown}`" + (f" — {part}" if part else ""))
        out.append("")
        for t in ([s["license_text"]] if "license_text" in s else []) + s.get("extra_texts", []):
            texts.append((s["name"], t))
    if texts:
        out.append("---\n")
        out.append("# License texts\n")
        for name, rel in texts:
            out.append(f"## {name} — {os.path.basename(rel)}\n")
            out.append("```text")
            out.append(read(rel).rstrip("\n"))
            out.append("```\n")
    return "\n".join(out).rstrip("\n") + "\n"


def plugins():
    base = os.path.join(ROOT, "plugins")
    return sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)))


def plan():
    """Return (files to write, generated notices that should no longer exist, problems)."""
    problems = []
    whole = {}
    protected = set()
    for s in SOURCES:
        for entry in s["paths"]:
            path, _ = split(entry)
            if not os.path.exists(os.path.join(ROOT, path)):
                problems.append(f"missing path listed in SOURCES: {path}")
        for rel in [s.get("license_file"), s.get("license_text"), *s.get("extra_texts", [])]:
            if rel and not os.path.exists(os.path.join(ROOT, rel)):
                problems.append(f"missing license file listed in SOURCES: {rel}")
        if s.get("license_file"):
            protected.add(s["license_file"])
        if s.get("whole_plugin"):
            (path, _), = map(split, s["paths"])
            whole[path] = s

    files = {NOTICES: render(SOURCES, None, HEADER.format(where="this repository"))}
    stale = []
    root_license = read("LICENSE")
    for name in plugins():
        base = f"plugins/{name}"
        if base not in whole:
            files[f"{base}/LICENSE"] = root_license
        used = [s for s in SOURCES if any(under(split(e)[0], base) for e in s["paths"])]
        notices = f"{base}/{NOTICES}"
        if used:
            header = HEADER_WHOLE_PLUGIN if base in whole else HEADER.format(where="this plugin")
            files[notices] = render(used, base, header)
        elif os.path.exists(os.path.join(ROOT, notices)):
            stale.append(notices)

    for rel in files:
        if rel in protected:
            problems.append(f"refusing to overwrite a third-party license file: {rel}")
        path = os.path.join(ROOT, rel)
        real_dir = os.path.realpath(os.path.dirname(path))
        if os.path.islink(path) or not (real_dir + os.sep).startswith(os.path.realpath(ROOT) + os.sep):
            problems.append(f"refusing to write through a symlink or outside the repo: {rel}")
    return files, stale, problems


def main():
    check = "--check" in sys.argv[1:]
    files, stale, problems = plan()
    if problems:
        for p in problems:
            print(p, file=sys.stderr)
        return 1
    for rel, content in files.items():
        path = os.path.join(ROOT, rel)
        current = open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if current == content:
            continue
        if check:
            problems.append(f"out of date: {rel}")
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"wrote {rel}")
    for rel in stale:
        if check:
            problems.append(f"stale (plugin has no third-party material): {rel}")
        else:
            os.remove(os.path.join(ROOT, rel))
            print(f"removed {rel}")
    for p in problems:
        print(p, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
