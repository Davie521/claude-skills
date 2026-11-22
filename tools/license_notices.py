#!/usr/bin/env python3
"""Generate the license files that ship with every plugin.

A plugin is installed from its own directory (plugins/<name>), so the root
LICENSE and THIRD_PARTY_NOTICES.md never reach the user's machine. This script
writes, from the SOURCES table below:

  THIRD_PARTY_NOTICES.md                    every third-party source in the repo
  plugins/<name>/LICENSE                    copy of the root LICENSE
  plugins/<name>/THIRD_PARTY_NOTICES.md     only the sources that plugin contains

Usage:
  python3 tools/license_notices.py          write the files
  python3 tools/license_notices.py --check  exit 1 if any file is out of date
                                            or a listed path no longer exists

When you migrate or graft material from another project, add it to SOURCES
and run the script.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Plugins that are entirely someone else's work and carry that author's LICENSE
# at the plugin root; the Licensor's LICENSE is not copied into them.
THIRD_PARTY_ONLY_PLUGINS = {"session-summary"}

# Each source: where it came from, its license, and the paths in this repo that
# contain its material. "license_file" is either a file under licenses/ whose
# full text is reproduced in the notices, or a path (relative to the repo root)
# of a license file that already sits next to the material.
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
            "plugins/business/skills/investor-materials",
            "plugins/code-review",
            "plugins/data/skills/data-scraper-agent",
            "plugins/data/skills/database-migrations",
            "plugins/dev-workflow/skills/deep-plan",
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
            "plugins/research/skills/research",
            "plugins/research/skills/search-routing",
            "plugins/skills/skills/rules-distill",
            "plugins/skills/skills/skill-comply",
            "plugins/skills/skills/skill-stocktake",
            "plugins/swift/skills/foundation-models-on-device",
            "plugins/swift/skills/liquid-glass-design",
            "plugins/swift/skills/swift-concurrency-6-2",
            "plugins/swift/skills/swiftui-patterns",
            "plugins/web/skills/api-design",
            "plugins/web/skills/bun-runtime",
            "plugins/web/skills/content-hash-cache-pattern",
            "plugins/web/skills/deployment-patterns",
            "plugins/web/skills/docker-patterns",
            "plugins/web/skills/mcp-server-patterns",
            "plugins/writing/skills/crosspost",
            "plugins/writing/skills/video-editing",
        ],
    },
    {
        "name": "mattpocock/skills",
        "url": "https://github.com/mattpocock/skills",
        "license": "MIT",
        "copyright": "Copyright (c) 2026 Matt Pocock",
        "license_text": "licenses/mattpocock-skills.MIT.txt",
        "note": "Copied and modified; each skill names its upstream path in an "
        "Origin footer. tdd-workflow only has a grafted section (see its "
        "Provenance footer).",
        "paths": [
            "plugins/dev-workflow/skills/caveman",
            "plugins/dev-workflow/skills/diagnose",
            "plugins/dev-workflow/skills/grill-with-docs",
            "plugins/dev-workflow/skills/improve-codebase-architecture",
            "plugins/dev-workflow/skills/prototype",
            "plugins/dev-workflow/skills/to-prd",
            "plugins/dev-workflow/skills/triage",
            "plugins/quality/skills/tdd-workflow",
        ],
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
        "name": "ui-ux-pro-max-skill",
        "url": "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill",
        "license": "MIT",
        "copyright": "Copyright (c) 2024 Next Level Builder",
        "license_file": "plugins/design/skills/ui-ux-pro-max/LICENSE",
        "note": "Copied and modified.",
        "paths": ["plugins/design/skills/ui-ux-pro-max"],
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
        "name": "anthropics/skills",
        "url": "https://github.com/anthropics/skills",
        "license": "Apache-2.0",
        "copyright": "Copyright Anthropic, PBC",
        "license_file": "plugins/document/skills/pdf/LICENSE.txt",
        "note": "Modified; the changes are listed in each skill's Origin "
        "section. doc-coauthoring carries its own copy of the license.",
        "paths": [
            "plugins/document/skills/doc-coauthoring",
            "plugins/document/skills/pdf",
        ],
    },
    {
        "name": "FlorianBruniaux/claude-code-plugins",
        "url": "https://github.com/FlorianBruniaux/claude-code-plugins",
        "license": "MIT",
        "copyright": "Copyright (c) 2026 Florian Bruniaux",
        "license_file": "plugins/session-summary/LICENSE",
        "note": "Vendored at 23883a1; the whole plugin is that author's work.",
        "paths": ["plugins/session-summary"],
    },
    {
        "name": "codebase-to-course",
        "url": "https://github.com/zarazhangrui/codebase-to-course",
        "license": "none published",
        "copyright": "all rights reserved by the author (Zara Zhang)",
        "note": "Adapted with changes. The author has published no license "
        "(see https://github.com/zarazhangrui/codebase-to-course/issues/10), "
        "so neither this collection's LICENSE nor any open-source grant "
        "covers it. It will be removed or relicensed if the author asks or "
        "publishes terms.",
        "paths": ["plugins/document/skills/codebase-to-course"],
    },
]

HEADER = """# Third-party notices

The Licensor's own work in {where} is licensed under the terms in `LICENSE`
(MIT with the Commons Clause). The material below comes from other authors and
stays under its original terms; neither the Licensor's LICENSE nor the Commons
Clause applies to it.
"""


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def plugin_of(path):
    parts = path.split("/")
    return parts[1] if len(parts) > 1 and parts[0] == "plugins" else None


def relative_to(path, base):
    return os.path.relpath(path, base) if base else path


HEADER_THIRD_PARTY_ONLY = """# Third-party notices

This plugin is another author's work, redistributed under its original license
(`LICENSE` in this directory). The Licensor's MIT-with-Commons-Clause terms do
not apply to it.
"""


def render(sources, base, where, header=None):
    out = [header or HEADER.format(where=where)]
    texts = []
    for s in sources:
        paths = [p for p in s["paths"] if base is None or p == base or p.startswith(base + "/")]
        out.append(f"## {s['name']}\n")
        out.append(f"- Source: {s['url']}")
        out.append(f"- License: {s['license']}, {s['copyright']}")
        if "license_file" in s:
            out.append(f"- License text: `{relative_to(s['license_file'], base)}`")
        elif "license_text" in s:
            out.append("- License text: reproduced at the end of this file")
        else:
            out.append("- License text: none")
        out.append(f"- {s['note']}")
        out.append("- Paths:")
        out.extend(f"  - `{relative_to(p, base) if p != base else '.'}`" for p in paths)
        out.append("")
        if "license_text" in s:
            texts.append((s["name"], read(s["license_text"]).rstrip("\n")))
    if texts:
        out.append("---\n")
        out.append("# License texts\n")
        for name, text in texts:
            out.append(f"## {name}\n")
            out.append("```text")
            out.append(text)
            out.append("```\n")
    return "\n".join(out).rstrip("\n") + "\n"


def wanted_files():
    files = {}
    files["THIRD_PARTY_NOTICES.md"] = render(SOURCES, None, "this repository")
    root_license = read("LICENSE")
    plugins = sorted(d for d in os.listdir(os.path.join(ROOT, "plugins"))
                     if os.path.isdir(os.path.join(ROOT, "plugins", d)))
    for name in plugins:
        base = f"plugins/{name}"
        if name not in THIRD_PARTY_ONLY_PLUGINS:
            files[f"{base}/LICENSE"] = root_license
        used = [s for s in SOURCES if any(p == base or p.startswith(base + "/") for p in s["paths"])]
        if used:
            header = HEADER_THIRD_PARTY_ONLY if name in THIRD_PARTY_ONLY_PLUGINS else None
            files[f"{base}/THIRD_PARTY_NOTICES.md"] = render(used, base, "this plugin", header)
    return files


def main():
    check = "--check" in sys.argv[1:]
    problems = []
    for s in SOURCES:
        for p in s["paths"] + [s.get("license_file"), s.get("license_text")]:
            if p and not os.path.exists(os.path.join(ROOT, p)):
                problems.append(f"missing path listed in SOURCES: {p}")
    for rel, content in wanted_files().items():
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
    for p in problems:
        print(p, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
