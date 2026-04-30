#!/usr/bin/env python3
"""Extract structured paper data from index.html for status checking.

Outputs a JSON list to stdout; one object per <li> entry under each <h2> +
<ol> block. Fields:
    title        plain-text title
    section      h2 heading (e.g. "Publications", "Working Papers & Work in Progress")
    section_id   h2 id attribute
    primary_url  href on the title link (None if title is unlinked)
    preprint_url href of the [Preprint] link if present
    citation     plain-text "(authors). YEAR/Forthcoming, Journal, vol (issue): pp."
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "index.html"

SECTION_RE = re.compile(
    r'<h2 id="([^"]+)">([^<]+)</h2>\s*<ol[^>]*>(.*?)</ol>',
    re.DOTALL,
)
LI_RE = re.compile(r"<li>(.*?)</li>", re.DOTALL)
TITLE_LINKED_RE = re.compile(
    r'<b>\s*<a\s+href="([^"]+)">\s*(.*?)\s*</a>\s*</b>',
    re.DOTALL,
)
TITLE_UNLINKED_RE = re.compile(r"<b>\s*([^<]+?)\s*</b>", re.DOTALL)
PREPRINT_RE = re.compile(
    r'<i>\s*<a\s+href="([^"]+)">\s*\[Preprint\]\s*</a>\s*</i>',
    re.DOTALL,
)
ABSTRACT_DIV_RE = re.compile(r'<div id="[^"]+"[^>]*>.*?</div>', re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")
SPLIT_RE = re.compile(r"<i>\s*<a|<br|<div\b")


def normalize(text: str) -> str:
    return WS_RE.sub(" ", html.unescape(text)).strip()


def extract_li(body: str, section: str):
    title_m = TITLE_LINKED_RE.search(body)
    if title_m:
        primary_url = title_m.group(1)
        title = normalize(title_m.group(2))
        after_idx = title_m.end()
    else:
        title_m = TITLE_UNLINKED_RE.search(body)
        if not title_m:
            return None
        primary_url = None
        title = normalize(title_m.group(1))
        after_idx = title_m.end()

    after = body[after_idx:]
    cleaned = ABSTRACT_DIV_RE.sub("", after)

    preprint_m = PREPRINT_RE.search(cleaned)
    preprint_url = preprint_m.group(1) if preprint_m else None

    cite_html = SPLIT_RE.split(cleaned, maxsplit=1)[0]
    citation = normalize(TAG_RE.sub("", cite_html))

    return {
        "title": title,
        "section": section,
        "primary_url": primary_url,
        "preprint_url": preprint_url,
        "citation": citation,
    }


def extract(html: str):
    out = []
    for m in SECTION_RE.finditer(html):
        section_id = m.group(1)
        section_name = normalize(m.group(2))
        ol_body = m.group(3)
        for li_m in LI_RE.finditer(ol_body):
            paper = extract_li(li_m.group(1), section_name)
            if paper:
                paper["section_id"] = section_id
                out.append(paper)
    return out


def main() -> int:
    if not INDEX.exists():
        print(f"index.html not found at {INDEX}", file=sys.stderr)
        return 1
    data = extract(INDEX.read_text(encoding="utf-8"))
    json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
